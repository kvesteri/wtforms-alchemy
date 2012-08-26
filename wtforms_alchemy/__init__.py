#import pytz
from wtforms import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FloatField,
    Form,
    FormField,
    IntegerField,
    TextAreaField,
    TextField,
    SelectField,
)
from wtforms.fields import Field, _unset_value
from wtforms.form import FormMeta
from wtforms.validators import Length, Optional, Required, ValidationError
from sqlalchemy import types
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.exc import NoResultFound


class Unique(object):
    """Checks field value unicity against specified table field.

    Currently only supports Flask-SQLAlchemy style models which have the query
    class.

    We must require models to have query class so that unique validators can be
    generated without the need of explicitly setting the SQLAlchemy session.

    :param model:
        The model to check unicity against.
    :param column:
        The unique column.
    :param message:
        The error message.
    """
    field_flags = ('unique', )

    def __init__(self, model, column, message=None):
        self.model = model
        self.column = column
        self.message = message

        if not hasattr(self.model, 'query'):
            raise Exception('Model classes must have query class.')

    def __call__(self, form, field):
        try:
            obj = (
                self.model.query
                .filter(self.column == field.data).one()
            )

            if not hasattr(form, '_obj') or not form._obj == obj:
                if self.message is None:
                    self.message = field.gettext(u'Already exists.')
                raise ValidationError(self.message)
        except NoResultFound:
            pass


class UnknownTypeException(Exception):
    pass


class FormGenerator(object):
    TYPE_MAP = {
        types.BigInteger: IntegerField,
        types.SmallInteger: IntegerField,
        types.Integer: IntegerField,
        types.DateTime: DateTimeField,
        types.Date: DateField,
        types.Text: TextAreaField,
        types.Unicode: TextField,
        types.UnicodeText: TextAreaField,
        types.Float: FloatField,
        types.Numeric: DecimalField,
        types.Boolean: BooleanField,
        types.Enum: SelectField,
    }

    def __init__(self,
                 model_class,
                 default=None,
                 assign_required=True,
                 validators={},
                 only_indexed_fields=False,
                 include_primary_keys=False,
                 include_foreign_keys=False,
                 all_fields_optional=False,
                 datetime_format=None,
                 date_format=None):
        self.validators = validators
        self.model_class = model_class
        self.default = default
        self.assign_required = assign_required
        self.only_indexed_fields = only_indexed_fields
        self.include_primary_keys = include_primary_keys
        self.include_foreign_keys = include_foreign_keys
        self.all_fields_optional = all_fields_optional
        self.datetime_format = datetime_format
        self.date_format = date_format

    def create_form(self, form, include=None, exclude=None):
        fields = set(self.model_class._sa_class_manager.values())
        tmp = []
        for field in fields:
            column = field.property
            if isinstance(column, ColumnProperty) and self.skip_column(column):
                continue
            tmp.append(field)
        fields = set(tmp)

        if include:
            fields.update(set(
                [getattr(self.model_class, field) for field in include]
            ))

        if exclude:
            func = lambda a: a.key not in exclude
            fields = filter(func, fields)

        return self.create_fields(form, fields)

    def create_fields(self, form, fields):
        for field in fields:
            column = field.property

            if not isinstance(column, ColumnProperty):
                continue

            name = column.columns[0].name
            form_field = self.create_field(column)

            if not hasattr(form, name):
                setattr(form, name, form_field)
        return form

    def skip_column(self, column_property):
        """Whether or not to skip column in the generation process."""
        column = column_property.columns[0]
        if (not self.include_primary_keys and column.primary_key or
                column.foreign_keys):
            return True

        if column_property._is_polymorphic_discriminator:
            return True

        if self.only_indexed_fields and not self.has_index(column):
            return True
        return False

    def has_index(self, column):
        if column.primary_key or column.foreign_keys:
            return True
        table = column.table
        for index in table.indexes:
            if len(index.columns) == 1 and column.name in index.columns:
                return True
        return False

    def create_field(self, column_property):
        column = column_property.columns[0]
        name = column.name
        validators = []
        kwargs = {}
        field_class = self.get_field_class(column.type)

        if self.all_fields_optional:
            validators.append(Optional())
        else:
            if column.default:
                kwargs['default'] = column.default.arg
            else:
                if not column.nullable:
                    kwargs['default'] = self.default

                if not column.nullable and self.assign_required:
                    validators.append(Required())
        validator = self.length_validator(column)
        if validator:
            validators.append(validator)

        if name in self.validators:
            if isinstance(self.validators[name], list):
                validators.extend(self.validators[name])
            else:
                validators.append(self.validators[name])

        if column.unique:
            validators.append(
                Unique(
                    self.model_class,
                    getattr(self.model_class, name)
                )
            )
        kwargs['validators'] = validators

        if hasattr(column.type, 'enums'):
            kwargs['choices'] = [(enum, enum) for enum in column.type.enums]

        if isinstance(column.type, types.DateTime):
            kwargs['format'] = self.datetime_format

        if isinstance(column.type, types.Date):
            kwargs['format'] = self.date_format

        return field_class(name, **kwargs)

    def length_validator(self, column):
        """
        Returns colander length validator for given column
        """
        if hasattr(column.type, 'length') and column.type.length:
            return Length(max=column.type.length)

    def get_field_class(self, column_type):
        for class_ in self.TYPE_MAP:
            # Float type in sqlalchemy inherits numeric type, hence we need
            # the following check
            if column_type.__class__ is types.Float:
                if isinstance(column_type, types.Float):
                    return self.TYPE_MAP[types.Float]
            if isinstance(column_type, class_):
                return self.TYPE_MAP[class_]
        raise UnknownTypeException(column_type)


def wtforms_decode_json(json):
    decoded = {}
    for key, value in json:
        if value is not False:
            continue
        elif isinstance(value, list):
            decoded[key] = [wtforms_decode_json(item) for item in value]
        elif isinstance(value, dict):
            decoded[key] = wtforms_decode_json(value)
        else:
            decoded[key] = value
    return decoded


def class_list(cls):
    list_of_parents = [cls]
    for parent in cls.__bases__:
        list_of_parents.extend(class_list(parent))
    return list_of_parents


def properties(cls):
    return dict((name, getattr(cls, name)) for name in dir(cls))


class ModelFormMeta(FormMeta):
    """Meta class that overrides WTForms base meta class. The primary purpose
    of this class is allowing ModelForms use special configuration params under
    the 'Meta' class namespace.

    ModelForm classes inherit parent's Meta class properties.
    """
    def __init__(cls, *args, **kwargs):
        property_dict = {}
        for class_ in reversed(class_list(cls)):
            if hasattr(class_, 'Meta'):
                property_dict.update(properties(class_.Meta))
        cls.Meta = type('Meta', (object, ), property_dict)

        return FormMeta.__init__(cls, *args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.Meta.model:
            generator = cls.Meta.form_generator(
                model_class=cls.Meta.model,
                default=cls.Meta.default,
                assign_required=cls.Meta.assign_required,
                validators=cls.Meta.validators,
                only_indexed_fields=cls.Meta.only_indexed_fields,
                include_primary_keys=cls.Meta.include_primary_keys,
                include_foreign_keys=cls.Meta.include_foreign_keys,
                all_fields_optional=cls.Meta.all_fields_optional,
                datetime_format=cls.Meta.datetime_format,
                date_format=cls.Meta.date_format
            )
            generator.create_form(cls, cls.Meta.include, cls.Meta.exclude)

        return FormMeta.__call__(cls, *args, **kwargs)


class ModelForm(Form):
    __metaclass__ = ModelFormMeta

    class Meta:
        model = None
        default = None

        #: Whether or not to assign non-nullable fields as required
        assign_required = True

        #: Whether or not to assign all fields as optional, useful when
        #: creating update forms
        all_fields_optional = False

        validators = {}

        #: Whether or not to include only indexed fields
        only_indexed_fields = False

        #: Whether or not to include primary keys.
        include_primary_keys = False

        #: Whether or not to include primary keys. By default this is False
        #: indicating that foreign keys are not included in the generated form.
        include_foreign_keys = False

        #: Which form generator to use. Only override this if you have a valid
        #: form generator which you want to use instead of the default one.
        form_generator = FormGenerator

        #: Default date format
        date_format = '%Y-%m-%d'

        #: Default datetime format
        datetime_format = '%Y-%m-%d %H:%M:%S'

        #: Additional fields to include in the generated form.
        include = []

        #: List of fields to exclude from the generated form.
        exclude = []

        #: List of fields to only include in the generated form.
        only = []

    def __init__(self, *args, **kwargs):
        """Sets object as form attribute."""

        if 'obj' in kwargs:
            self._obj = kwargs['obj']
        super(ModelForm, self).__init__(*args, **kwargs)

    @property
    def patch_data(self):
        data = {}
        for name, f in self._fields.iteritems():
            if not f.is_unset:
                data[name] = f.data
        return data


def monkey_patch_process(func):
    def process(self, formdata, data=_unset_value):
        if data is _unset_value:
            self.is_unset = True
        else:
            self.is_unset = False
        func(self, formdata, data=data)
    return process


Field.process = monkey_patch_process(Field.process)
FormField.process = monkey_patch_process(FormField.process)


class ModelCreateForm(ModelForm):
    pass


class ModelUpdateForm(ModelForm):
    class Meta:
        all_fields_optional = True
        assign_required = False


class ModelSearchForm(ModelForm):
    class Meta:
        all_fields_optional = True
        only_indexed_fields = True
        include_primary_keys = True
