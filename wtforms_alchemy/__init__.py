#import pytz
from decimal import Decimal
from wtforms import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FloatField,
    Form,
    IntegerField,
    TextAreaField,
    TextField,
)
from wtforms.fields import FormField, FieldList
from wtforms.form import FormMeta
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
)
from sqlalchemy import types
from sqlalchemy.orm import object_session
from sqlalchemy.orm.util import has_identity
from sqlalchemy.orm.properties import ColumnProperty
from wtforms_components import (
    SelectField,
    SelectMultipleField,
    DateRange,
    Unique,
)
from .utils import (
    is_date_column,
    is_integer_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
)


__all__ = (
    DateRange,
    SelectMultipleField,
    Unique,
    is_date_column,
    is_integer_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
)


class UnknownTypeException(Exception):
    def __init__(self, column):
        Exception.__init__(
            self,
            "Unknown type '%s' for column '%s'" %
            (column.type, column.name)
        )


class InvalidAttributeException(Exception):
    def __init__(self, attr_name):
        Exception.__init__(
            self,
            "Model attribute '%s' is not a valid sqlalchemy column." %
            attr_name
        )


class FormGenerator(object):
    """
    Base form generator, you can make your own form generators by inheriting
    this class.
    """
    TYPE_MAP = {
        types.BigInteger: IntegerField,
        types.SmallInteger: IntegerField,
        types.Integer: IntegerField,
        types.DateTime: DateTimeField,
        types.Date: DateField,
        types.Text: TextAreaField,
        types.Unicode: TextField,
        types.UnicodeText: TextAreaField,
        types.String: TextField,
        types.Float: FloatField,
        types.Numeric: DecimalField,
        types.Boolean: BooleanField,
        types.Enum: SelectField,
    }

    COERCE_TYPE_MAP = {
        types.BigInteger: int,
        types.SmallInteger: int,
        types.Integer: int,
        types.Text: str,
        types.Unicode: unicode,
        types.UnicodeText: unicode,
        types.String: str,
        types.Float: float,
        types.Numeric: Decimal,
    }

    def __init__(self, form_class):
        """
        Initializes the form generator

        :param form_class: ModelForm class to be used as the base of generation
                           process
        """
        self.form_class = form_class
        self.model_class = self.form_class.Meta.model
        self.meta = self.form_class.Meta

    def create_form(self, form):
        """
        Creates the form.

        :param form: ModelForm instance
        """
        fields = set(self.model_class._sa_class_manager.values())
        tmp = []
        for field in fields:
            column = field.property
            if not isinstance(column, ColumnProperty):
                continue
            if self.skip_column(column):
                continue
            tmp.append(field)
        fields = set(tmp)

        def valid_attribute(attr_name):
            attr = getattr(self.model_class, attr_name)
            if not hasattr(attr, 'property'):
                raise InvalidAttributeException(attr_name)

            if not isinstance(attr.property, ColumnProperty):
                raise InvalidAttributeException(attr_name)

            return attr

        if self.meta.only:
            fields = set(map(valid_attribute, self.meta.only))
        else:
            if self.meta.include:
                fields.update(map(valid_attribute, self.meta.include))

            if self.meta.exclude:
                func = lambda a: a.key not in self.meta.exclude
                fields = filter(func, fields)

        return self.create_fields(form, fields)

    def create_fields(self, form, attributes):
        """
        Creates fields for given form based on given model attributes.

        :param form: form to attach the generated fields into
        :param attributes: model attributes to generate the form fields from
        """
        for attribute in attributes:
            column = attribute.property

            name = column.columns[0].name
            form_field = self.create_field(column)

            if not hasattr(form, name):
                setattr(form, name, form_field)
        return form

    def skip_column(self, column_property):
        """
        Whether or not to skip column in the generation process.

        :param column_property: SQLAlchemy ColumnProperty object
        """
        column = column_property.columns[0]
        if (not self.meta.include_primary_keys and column.primary_key or
                column.foreign_keys):
            return True

        if column_property._is_polymorphic_discriminator:
            return True

        if (not self.meta.include_datetimes_with_default and
                isinstance(column.type, types.DateTime) and
                column.default):
            return True

        if self.meta.only_indexed_fields and not self.has_index(column):
            return True
        return False

    def has_index(self, column):
        """
        Whether or not given column has an index.

        :param column: Column object to inspect the indexes from
        """
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
        kwargs = {}
        field_class = self.get_field_class(column)

        if column.default and is_scalar(column.default.arg):
            kwargs['default'] = column.default.arg
        else:
            if not column.nullable:
                kwargs['default'] = self.meta.default

        validators = self.create_validators(column)
        kwargs['validators'] = validators

        if 'description' in column.info:
            kwargs['description'] = column.info['description']

        if 'label' in column.info:
            kwargs['label'] = column.info['label']
        else:
            kwargs['label'] = name

        if (hasattr(column.type, 'enums') or
                ('choices' in column.info and column.info['choices'])):
            kwargs = self.select_field_kwargs(column, kwargs)

        if isinstance(column.type, types.DateTime):
            kwargs['format'] = self.meta.datetime_format

        if isinstance(column.type, types.Date):
            kwargs['format'] = self.meta.date_format

        return field_class(**kwargs)

    def select_field_kwargs(self, column, kwargs):
        """
        Create key value args for SelectField based on SQLAlchemy column
        definitions.
        """
        kwargs['coerce'] = null_or_unicode
        if column.type.__class__ in self.COERCE_TYPE_MAP:
            coerce_func = self.COERCE_TYPE_MAP[column.type.__class__]
            kwargs['coerce'] = coerce_func
            if column.nullable and kwargs['coerce'] in (unicode, str):
                kwargs['coerce'] = null_or_unicode

        if 'choices' in column.info and column.info['choices']:
            kwargs['choices'] = column.info['choices']
        else:
            kwargs['choices'] = [
                (enum, enum) for enum in column.type.enums
            ]
        return kwargs

    def create_validators(self, column):
        """
        Creates validators for given column
        """
        validators = [
            self.required_validator(column),
            self.length_validator(column),
            self.unique_validator(column),
            self.range_validator(column)
        ]
        validators = [v for v in validators if v is not None]
        validators.extend(self.additional_validators(column))
        return validators

    def required_validator(self, column):
        """
        Returns required / optional validator for given column based on column
        nullability and form configuration.
        """
        if (not self.meta.all_fields_optional and
            not column.default and
            not column.nullable and
            self.meta.assign_required and not
                isinstance(column.type, types.Boolean)):
            return DataRequired()
        return Optional()

    def additional_validators(self, column):
        """
        Returns additional validators for given column
        """
        validators = []
        name = column.name
        if name in self.meta.validators:
            try:
                validators.extend(self.meta.validators[name])
            except TypeError:
                validators.append(self.meta.validators[name])

        if 'validators' in column.info and column.info['validators']:
            try:
                validators.extend(column.info['validators'])
            except TypeError:
                validators.append(column.info['validators'])
        return validators

    def unique_validator(self, column):
        """
        Returns unique validator for given column if column has a unique index
        """
        if column.unique:
            return Unique(
                getattr(self.model_class, column.name),
                get_session=self.form_class.get_session
            )

    def range_validator(self, column):
        """
        Returns range validator based on column type and column info min and
        max arguments
        """
        min_ = column.info.get('min', None)
        max_ = column.info.get('max', None)

        if min_ or max_:
            if is_integer_column(column):
                return NumberRange(min=min_, max=max_)
            elif is_date_column(column):
                return DateRange(min=min_, max=max_)

    def length_validator(self, column):
        """
        Returns length validator for given column
        """
        if hasattr(column.type, 'length') and column.type.length:
            return Length(max=column.type.length)

    def get_field_class(self, column):
        """
        Returns WTForms field class. Class is based on a custom field class
        attribute or SQLAlchemy column type.
        """
        if ('form_field_class' in column.info
                and column.info['form_field_class']):
            return column.info['form_field_class']
        if 'choices' in column.info and column.info['choices']:
            return SelectField
        if column.type.__class__ not in self.TYPE_MAP:
            raise UnknownTypeException(column)
        return self.TYPE_MAP[column.type.__class__]


def class_list(cls):
    """Simple recursive function for listing the parent classes of given class.
    Used by the ModelFormMeta class.
    """
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
            generator = cls.Meta.form_generator(cls)
            generator.create_form(cls)

        return FormMeta.__call__(cls, *args, **kwargs)


def model_form_factory(base=Form):
    """Creates new model form, with given base class."""

    class ModelForm(base):
        __metaclass__ = ModelFormMeta

        """
        A function that returns SQLAlchemy session. This should be
        assigned if you wish to use Unique validator. If you are using
        Flask-SQLAlchemy along with WTForms-Alchemy you don't need to
        set this.
        """
        get_session = None

        class Meta:
            model = None

            default = None

            #: Whether or not to assign non-nullable fields as required
            assign_required = True

            #: Whether or not to assign all fields as optional, useful when
            #: creating update forms for patch requests
            all_fields_optional = False

            validators = {}

            #: Whether or not to include only indexed fields.
            only_indexed_fields = False

            #: Whether or not to include primary keys.
            include_primary_keys = False

            #: Whether or not to include foreign keys. By default this is False
            #: indicating that foreign keys are not included in the generated
            #: form.
            include_foreign_keys = False

            #: Whether or not to include datetime columns that have a default
            #: value. A good example is created_at column which has a default
            #: value of datetime.utcnow.
            include_datetimes_with_default = False

            #: Which form generator to use. Only override this if you have a
            #: valid form generator which you want to use instead of the
            #: default one.
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

    return ModelForm


def session(obj):
    session = object_session(obj)
    if not session:
        raise Exception(
            'Object %s is not bound the session. Use session.add() to '
            'add this object into session.' % str(obj)
        )
    return session


class SkipOperation(Exception):
    pass


class ModelFormField(FormField):
    def populate_obj(self, obj, name):
        if has_identity(obj):
            sess = session(obj)
            item = getattr(obj, name, None)
            if item:
                # only delete persistent objects
                if has_identity(item):
                    sess.delete(item)
                elif item in sess:
                    sess.expunge(item)
                setattr(obj, name, None)

        if self.data:
            setattr(obj, name, self.form.Meta.model())

        FormField.populate_obj(self, obj, name)


class ModelFieldList(FieldList):
    def pre_append_object(self, obj, name, counter):
        pass

    def delete_existing(self, obj, name):
        if has_identity(obj):
            sess = session(obj)
            items = getattr(obj, name, set([]))
            while items:
                item = items.pop()
                # only delete persistent objects
                if has_identity(item):
                    sess.delete(item)

    def populate_obj(self, obj, name):
        self.delete_existing(obj, name)

        model = self.unbound_field.args[0].Meta.model
        for counter in xrange(len(self.entries)):
            try:
                self.pre_append_object(obj, name, counter)
                try:
                    getattr(obj, name).append(model())
                except AttributeError:
                    pass
            except SkipOperation:
                pass
        FieldList.populate_obj(self, obj, name)


ModelForm = model_form_factory(Form)


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
