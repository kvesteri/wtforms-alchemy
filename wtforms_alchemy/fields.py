import operator
from itertools import groupby

import sqlalchemy as sa
from sqlalchemy.orm.util import identity_key
from sqlalchemy_utils import Country, i18n, PhoneNumber
from sqlalchemy_utils.primitives import WeekDay, WeekDays
from wtforms import widgets
from wtforms.fields import FieldList, FormField, SelectFieldBase
from wtforms.utils import unset_value
from wtforms.validators import ValidationError
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms_components import SelectField, SelectMultipleField
from wtforms_components.fields.html5 import StringField
from wtforms_components.widgets import SelectWidget, TelInput

from .utils import find_entity


class SkipOperation(Exception):
    pass


class ModelFormField(FormField):
    def populate_obj(self, obj, name):
        if self.data:
            try:
                if getattr(obj, name) is None:
                    setattr(obj, name, self.form.Meta.model())
            except AttributeError:
                pass
        FormField.populate_obj(self, obj, name)


class ModelFieldList(FieldList):
    def __init__(self, unbound_field, population_strategy="update", **kwargs):
        self.population_strategy = population_strategy
        super().__init__(unbound_field, **kwargs)

    @property
    def model(self):
        return self.unbound_field.args[0].Meta.model

    def _get_bound_field_for_entry(self, formdata, data, index):
        assert (
            not self.max_entries or len(self.entries) < self.max_entries
        ), "You cannot have more than max_entries entries in this FieldList"
        new_index = self.last_index = index or (self.last_index + 1)
        name = "%s-%d" % (self.short_name, new_index)
        id = "%s-%d" % (self.id, new_index)
        return self.unbound_field.bind(
            form=None, name=name, prefix=self._prefix, id=id, _meta=self.meta
        )

    def _add_entry(self, formdata=None, data=unset_value, index=None):
        field = self._get_bound_field_for_entry(
            formdata=formdata, data=data, index=index
        )
        if data != unset_value and data:
            if formdata:
                field.process(formdata)
            else:
                field.process(formdata, data=data)

            entity = find_entity(self.object_data, self.model, field.data)
            if entity is not None:
                field.process(formdata, entity)
        else:
            field.process(formdata)

        self.entries.append(field)
        return field

    def populate_obj(self, obj, name):
        state = sa.inspect(obj)

        if not state.identity or self.population_strategy == "replace":
            setattr(obj, name, [])
            for counter in range(len(self.entries)):
                try:
                    getattr(obj, name).append(self.model())
                except AttributeError:
                    pass
        else:
            coll = getattr(obj, name)
            entities = []
            for index, entry in enumerate(self.entries):
                data = entry.data
                entity = find_entity(coll, self.model, data)
                if entity is None:
                    entities.insert(index, self.model())
                else:
                    entities.append(entity)
            setattr(obj, name, entities)
        FieldList.populate_obj(self, obj, name)


class CountryField(SelectField):
    def __init__(self, *args, **kwargs):
        kwargs["coerce"] = Country
        super().__init__(*args, **kwargs)
        self.choices = self._get_choices

    def _get_choices(self):
        # Get all territories and filter out continents (3-digit code)
        # and some odd territories such as "Unknown or Invalid Region"
        # ("ZZ"), "European Union" ("QU") and "Outlying Oceania" ("QO").
        territories = [
            (code, name)
            for code, name in i18n.get_locale().territories.items()
            if len(code) == 2 and code not in ("QO", "QU", "ZZ")
        ]
        return sorted(territories, key=operator.itemgetter(1))


class QuerySelectField(SelectFieldBase):
    """
    Will display a select drop-down field to choose between ORM results in a
    sqlalchemy `Query`.  The `data` property actually will store/keep an ORM
    model instance, not the ID. Submitting a choice which is not in the query
    will result in a validation error.
    This field only works for queries on models whose primary key column(s)
    have a consistent string representation. This means it mostly only works
    for those composed of string, unicode, and integer types. For the most
    part, the primary keys will be auto-detected from the model, alternately
    pass a one-argument callable to `get_pk` which can return a unique
    comparable key.
    The `query` property on the field can be set from within a view to assign
    a query per-instance to the field. If the property is not set, the
    `query_factory` callable passed to the field constructor will be called to
    obtain a query.
    Specify `get_label` to customize the label associated with each option. If
    a string, this is the name of an attribute on the model object to use as
    the label text. If a one-argument callable, this callable will be passed
    model instance and expected to return the label text. Otherwise, the model
    object's `__str__` or `__unicode__` will be used.
    If `allow_blank` is set to `True`, then a blank choice will be added to the
    top of the list. Selecting this choice will result in the `data` property
    being `None`. The label for this blank choice can be set by specifying the
    `blank_text` parameter.
    """

    widget = widgets.Select()

    def __init__(
        self,
        label=None,
        validators=None,
        query_factory=None,
        get_pk=None,
        get_label=None,
        allow_blank=False,
        blank_text="",
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        self.query_factory = query_factory

        if get_pk is None:
            self.get_pk = get_pk_from_identity
        else:
            self.get_pk = get_pk

        if get_label is None:
            self.get_label = lambda x: x
        elif isinstance(get_label, str):
            self.get_label = operator.attrgetter(get_label)
        else:
            self.get_label = get_label

        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self.query = None
        self._object_list = None

    def _get_data(self):
        if self._formdata is not None:
            for pk, obj in self._get_object_list():
                if pk == self._formdata:
                    self._set_data(obj)
                    break
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def _get_object_list(self):
        if self._object_list is None:
            query = self.query if self.query is not None else self.query_factory()
            get_pk = self.get_pk
            self._object_list = list((str(get_pk(obj)), obj) for obj in query)
        return self._object_list

    def iter_choices(self):
        if self.allow_blank:
            yield ("__None", self.blank_text, self.data is None, {})

        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj == self.data, {})

    def process_formdata(self, valuelist):
        if valuelist:
            if self.allow_blank and valuelist[0] == "__None":
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]

    def pre_validate(self, form):
        data = self.data
        if data is not None:
            for pk, obj in self._get_object_list():
                if data == obj:
                    break
            else:
                raise ValidationError(self.gettext("Not a valid choice"))
        elif self._formdata or not self.allow_blank:
            raise ValidationError(self.gettext("Not a valid choice"))


class QuerySelectMultipleField(QuerySelectField):
    """
    Very similar to QuerySelectField with the difference that this will
    display a multiple select. The data property will hold a list with ORM
    model instances and will be an empty list when no value is selected.
    If any of the items in the data list or submitted form data cannot be
    found in the query, this will result in a validation error.
    """

    widget = widgets.Select(multiple=True)

    def __init__(self, label=None, validators=None, default=None, **kwargs):
        if default is None:
            default = []
        super().__init__(label, validators, default=default, **kwargs)
        if kwargs.get("allow_blank", False):
            import warnings

            warnings.warn(
                "allow_blank=True does not do anything for " "QuerySelectMultipleField."
            )
        self._invalid_formdata = False

    def _get_data(self):
        formdata = self._formdata
        if formdata is not None:
            data = []
            for pk, obj in self._get_object_list():
                if not formdata:
                    break
                elif pk in formdata:
                    formdata.remove(pk)
                    data.append(obj)
            if formdata:
                self._invalid_formdata = True
            self._set_data(data)
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def iter_choices(self):
        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj in self.data, {})

    def process_formdata(self, valuelist):
        self._formdata = set(valuelist)

    def pre_validate(self, form):
        if self._invalid_formdata:
            raise ValidationError(self.gettext("Not a valid choice"))
        elif self.data:
            obj_list = list(x[1] for x in self._get_object_list())
            for v in self.data:
                if v not in obj_list:
                    raise ValidationError(self.gettext("Not a valid choice"))


def get_pk_from_identity(obj):
    cls, key = identity_key(instance=obj)[0:2]
    return ":".join(str(x) for x in key)


class GroupedQuerySelectField(SelectField):
    widget = SelectWidget()

    def __init__(
        self,
        label=None,
        validators=None,
        query_factory=None,
        get_pk=None,
        get_label=None,
        get_group=None,
        allow_blank=False,
        blank_text="",
        blank_value="__None",
        **kwargs,
    ):
        super().__init__(label, validators, coerce=lambda x: x, **kwargs)

        self.query = None
        self.query_factory = query_factory

        if get_pk is None:
            self.get_pk = get_pk_from_identity
        else:
            self.get_pk = get_pk

        self.get_label = get_label
        self.get_group = get_group

        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self.blank_value = blank_value

        self._choices = None

    def _get_object_list(self):
        query = self.query if self.query is not None else self.query_factory()
        return list((str(self.get_pk(obj)), obj) for obj in query)

    def _pre_process_object_list(self, object_list):
        return sorted(
            object_list, key=lambda x: (x[1] or "", self.get_label(x[2]) or "")
        )

    @property
    def choices(self):
        if not self._choices:
            object_list = map(
                lambda x: (x[0], self.get_group(x[1]), x[1]), self._get_object_list()
            )
            # object_list is (key, group, value) tuple
            choices = [(self.blank_value, self.blank_text)] if self.allow_blank else []
            object_list = self._pre_process_object_list(object_list)
            for group, data in groupby(object_list, key=lambda x: x[1]):
                if group is not None:
                    group_items = []
                    for key, _, value in data:
                        group_items.append((key, self.get_label(value)))
                    choices.append((group, group_items))
                else:
                    for key, group, value in data:
                        choices.append((key, self.get_label(value)))
            self._choices = choices
        return self._choices

    @choices.setter
    def choices(self, value):
        pass

    @property
    def data(self):
        if self._formdata is not None:
            for pk, obj in self._get_object_list():
                if pk == self._formdata:
                    self.data = obj
                    break
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._formdata = None

    def iter_choices(self):
        """
        We should update how choices are iter to make sure that value from
        internal list or tuple should be selected.
        """
        for value, label in self.concrete_choices:
            yield (
                value,
                label,
                (
                    self.coerce,
                    self.get_pk(self.data) if self.data else self.blank_value,
                ),
                {},
            )

    def process_formdata(self, valuelist):
        if valuelist:
            if self.allow_blank and valuelist[0] == self.blank_value:
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]

    def pre_validate(self, form):
        data = self.data
        if data is not None:
            for pk, obj in self._get_object_list():
                if data == obj:
                    break
            else:
                raise ValidationError("Not a valid choice")
        elif self._formdata or not self.allow_blank:
            raise ValidationError("Not a valid choice")


class GroupedQuerySelectMultipleField(SelectField):
    widget = SelectWidget(multiple=True)

    def __init__(
        self,
        label=None,
        validators=None,
        query_factory=None,
        get_pk=None,
        get_label=None,
        get_group=None,
        blank_text="",
        default=None,
        **kwargs,
    ):
        if default is None:
            default = []
        super().__init__(
            label, validators, default=default, coerce=lambda x: x, **kwargs
        )
        if kwargs.get("allow_blank", False):
            import warnings

            warnings.warn(
                "allow_blank=True does not do anything for "
                "GroupedQuerySelectMultipleField."
            )

        self.query = None
        self.query_factory = query_factory

        if get_pk is None:
            self.get_pk = get_pk_from_identity
        else:
            self.get_pk = get_pk

        self.get_label = get_label
        self.get_group = get_group

        self.blank_text = blank_text

        self._choices = None
        self._invalid_formdata = False

    def _get_object_list(self):
        query = self.query if self.query is not None else self.query_factory()
        return list((str(self.get_pk(obj)), obj) for obj in query)

    def _pre_process_object_list(self, object_list):
        return sorted(
            object_list, key=lambda x: (x[1] or "", self.get_label(x[2]) or "")
        )

    @property
    def choices(self):
        if not self._choices:
            object_list = map(
                lambda x: (x[0], self.get_group(x[1]), x[1]), self._get_object_list()
            )
            # object_list is (key, group, value) tuple
            choices = []
            object_list = self._pre_process_object_list(object_list)
            for group, data in groupby(object_list, key=lambda x: x[1]):
                if group is not None:
                    group_items = []
                    for key, _, value in data:
                        group_items.append((key, self.get_label(value)))
                    choices.append((group, group_items))
                else:
                    for key, group, value in data:
                        choices.append((key, self.get_label(value)))
            self._choices = choices
        return self._choices

    @choices.setter
    def choices(self, value):
        pass

    @property
    def data(self):
        formdata = self._formdata
        if formdata is not None:
            data = []
            for pk, obj in self._get_object_list():
                if not formdata:
                    break
                elif self.coerce(pk) in formdata:
                    formdata.remove(self.coerce(pk))
                    data.append(obj)
            if formdata:
                self._invalid_formdata = True
            self.data = data
        return self._data

    @data.setter
    def data(self, valuelist):
        self._data = valuelist
        self._formdata = None

    def iter_choices(self):
        """
        We should update how choices are iter to make sure that value from
        internal list or tuple should be selected.
        """
        for value, label in self.concrete_choices:
            yield (
                value,
                label,
                (self.coerce, [self.get_pk(obj) for obj in self.data or []]),
                {},
            )

    def process_formdata(self, valuelist):
        self._formdata = set(valuelist)

    def pre_validate(self, form):
        self.data  # This sets self._invalid_formdata
        if self._invalid_formdata:
            raise ValidationError(self.gettext("Not a valid choice"))
        elif self.data:
            obj_list = list(x[1] for x in self._get_object_list())
            for v in self.data:
                if v not in obj_list:
                    raise ValidationError(self.gettext("Not a valid choice"))


class WeekDaysField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

    def __init__(self, *args, **kwargs):
        kwargs["coerce"] = lambda x: WeekDay(int(x))
        super().__init__(*args, **kwargs)
        self.choices = self._get_choices

    def _get_choices(self):
        days = WeekDays("1111111")
        for day in days:
            yield day.index, day.get_name(context="stand-alone")

    def process_data(self, value):
        self.data = WeekDays(value) if value else None

    def process_formdata(self, valuelist):
        self.data = WeekDays(self.coerce(x) for x in valuelist)

    def pre_validate(self, form):
        pass


class PhoneNumberField(StringField):
    """
    A string field representing a PhoneNumber object from
    `SQLAlchemy-Utils`_.

    .. _SQLAlchemy-Utils:
       https://github.com/kvesteri/sqlalchemy-utils

    :param region:
        Country code of the phone number.
    :param display_format:
        The format in which the phone number is displayed.
    """

    widget = TelInput()
    error_msg = "Not a valid phone number value"

    def __init__(
        self,
        label=None,
        validators=None,
        region="US",
        display_format="national",
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        self.region = region
        self.display_format = display_format

    def _value(self):
        # self.data holds a PhoneNumber object if the form is valid,
        # otherwise it will contain a string.
        if self.data:
            try:
                return getattr(self.data, self.display_format)
            except AttributeError:
                return self.data
        else:
            return ""

    def process_formdata(self, valuelist):
        import phonenumbers

        if valuelist:
            if valuelist[0] == "":
                self.data = None
            else:
                self.data = valuelist[0]
                try:
                    self.data = PhoneNumber(valuelist[0], self.region)
                    if not self.data.is_valid_number():
                        raise ValueError(self.gettext(self.error_msg))
                except phonenumbers.phonenumberutil.NumberParseException:
                    raise ValueError(self.gettext(self.error_msg))
