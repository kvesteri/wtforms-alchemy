try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
import inspect
from decimal import Decimal

import six
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy_utils import types
from wtforms import (
    BooleanField,
    Field,
    FloatField,
    PasswordField,
    TextAreaField
)
from wtforms.widgets import CheckboxInput, TextArea
from wtforms_components import (
    ColorField,
    DateField,
    DateIntervalField,
    DateTimeField,
    DateTimeIntervalField,
    DateTimeLocalField,
    DecimalField,
    DecimalIntervalField,
    EmailField,
    IntegerField,
    IntIntervalField,
    SelectField,
    StringField,
    TimeField
)
from wtforms_components.widgets import (
    ColorInput,
    DateInput,
    DateTimeInput,
    DateTimeLocalInput,
    EmailInput,
    NumberInput,
    TextInput,
    TimeInput
)

from .exc import (
    AttributeTypeException,
    InvalidAttributeException,
    UnknownTypeException
)
from .fields import CountryField, PhoneNumberField, WeekDaysField
from .utils import (
    choice_type_coerce_factory,
    ClassMap,
    flatten,
    is_date_column,
    is_number,
    is_number_range,
    is_scalar,
    null_or_unicode,
    strip_string,
    translated_attributes
)


class FormGenerator(object):
    """
    Base form generator, you can make your own form generators by inheriting
    this class.
    """

    # When converting SQLAlchemy types to fields this ordered dict is iterated
    # in given order. This allows smart type conversion of different inherited
    # type objects.
    TYPE_MAP = ClassMap((
        (sa.types.UnicodeText, TextAreaField),
        (sa.types.BigInteger, IntegerField),
        (sa.types.SmallInteger, IntegerField),
        (sa.types.Text, TextAreaField),
        (sa.types.Boolean, BooleanField),
        (sa.types.Date, DateField),
        (sa.types.DateTime, DateTimeField),
        (sa.types.Enum, SelectField),
        (sa.types.Float, FloatField),
        (sa.types.Integer, IntegerField),
        (sa.types.Numeric, DecimalField),
        (sa.types.Unicode, StringField),
        (sa.types.String, StringField),
        (sa.types.Time, TimeField),
        (postgresql.ARRAY, DecimalField),
        (postgresql.JSON, DecimalField),
        (types.ArrowType, DateTimeField),
        (types.ChoiceType, SelectField),
        (types.ColorType, ColorField),
        (types.CountryType, CountryField),
        (types.DateRangeType, DateIntervalField),
        (types.DateTimeRangeType, DateTimeIntervalField),
        (types.EmailType, EmailField),
        (types.IntRangeType, IntIntervalField),
        (types.NumericRangeType, DecimalIntervalField),
        (types.PasswordType, PasswordField),
        (types.PhoneNumberType, PhoneNumberField),
        (types.ScalarListType, StringField),
        (types.URLType, StringField),
        (types.UUIDType, StringField),
        (types.WeekDaysType, WeekDaysField),
    ))

    WIDGET_MAP = OrderedDict((
        (BooleanField, CheckboxInput),
        (ColorField, ColorInput),
        (DateField, DateInput),
        (DateTimeField, DateTimeInput),
        (DateTimeLocalField, DateTimeLocalInput),
        (DecimalField, NumberInput),
        (EmailField, EmailInput),
        (FloatField, NumberInput),
        (IntegerField, NumberInput),
        (TextAreaField, TextArea),
        (TimeField, TimeInput),
        (StringField, TextInput)
    ))

    def __init__(self, form_class):
        """
        Initializes the form generator

        :param form_class: ModelForm class to be used as the base of generation
                           process
        """
        self.form_class = form_class
        self.model_class = self.form_class.Meta.model
        self.meta = self.form_class.Meta
        self.TYPE_MAP.update(self.form_class.Meta.type_map)

    def create_form(self, form):
        """
        Creates the form.

        :param form: ModelForm instance
        """
        attrs = OrderedDict()
        for key, property_ in sa.inspect(self.model_class).attrs.items():
            if not isinstance(property_, ColumnProperty):
                continue
            if self.skip_column_property(property_):
                continue
            attrs[key] = property_

        for attr in translated_attributes(self.model_class):
            attrs[attr.key] = attr.property

        return self.create_fields(form, self.filter_attributes(attrs))

    def filter_attributes(self, attrs):
        """
        Filter set of model attributes based on only, exclude and include
        meta parameters.

        :param attrs: Set of attributes
        """
        if self.meta.only:
            attrs = OrderedDict([
                (key, prop)
                for key, prop in map(self.validate_attribute, self.meta.only)
                if key
            ])
        else:
            if self.meta.include:
                attrs.update([
                    (key, prop)
                    for key, prop
                    in map(self.validate_attribute, self.meta.include)
                    if key
                ])

            if self.meta.exclude:
                for key in self.meta.exclude:
                    try:
                        del attrs[key]
                    except KeyError:
                        if self.meta.attr_errors:
                            raise InvalidAttributeException(key)
        return attrs

    def validate_attribute(self, attr_name):
        """
        Finds out whether or not given sqlalchemy model attribute name is
        valid. Returns attribute property if valid.

        :param attr_name: Attribute name
        """
        try:
            attr = getattr(self.model_class, attr_name)
        except AttributeError:
            try:
                translation_class = (
                    self.model_class.__translatable__['class']
                )
                attr = getattr(translation_class, attr_name)
            except AttributeError:
                if self.meta.attr_errors:
                    raise InvalidAttributeException(attr_name)
                else:
                    return None, None
        try:
            if not isinstance(attr.property, ColumnProperty):
                if self.meta.attr_errors:
                    raise InvalidAttributeException(attr_name)
                else:
                    return None, None
        except AttributeError:
            raise AttributeTypeException(attr_name)
        return attr_name, attr.property

    def create_fields(self, form, properties):
        """
        Creates fields for given form based on given model attributes.

        :param form: form to attach the generated fields into
        :param attributes: model attributes to generate the form fields from
        """
        for key, prop in properties.items():
            column = prop.columns[0]
            try:
                field = self.create_field(prop, column)
            except UnknownTypeException:
                if not self.meta.skip_unknown_types:
                    raise
                else:
                    continue

            if not hasattr(form, key):
                setattr(form, key, field)

    def skip_column_property(self, column_property):
        """
        Whether or not to skip column property in the generation process.

        :param column_property: SQLAlchemy ColumnProperty object
        """
        if column_property._is_polymorphic_discriminator:
            return True

        return self.skip_column(column_property.columns[0])

    def skip_column(self, column):
        """
        Whether or not to skip column in the generation process.

        :param column_property: SQLAlchemy Column object
        """
        if not self.meta.include_foreign_keys and column.foreign_keys:
            return True

        if not self.meta.include_primary_keys and column.primary_key:
            return True

        if (not self.meta.include_datetimes_with_default and
                isinstance(column.type, sa.types.DateTime) and
                column.default):
            return True

        if isinstance(column.type, types.TSVectorType):
            return True

        if self.meta.only_indexed_fields and not self.has_index(column):
            return True

        # Skip all non columns (this is the case when using column_property
        # methods).
        if not isinstance(column, sa.Column):
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

    def create_field(self, prop, column):
        """
        Create form field for given column.

        :param prop: SQLAlchemy ColumnProperty object.
        :param column: SQLAlchemy Column object.
        """
        kwargs = {}
        field_class = self.get_field_class(column)
        kwargs['default'] = self.default(column)
        kwargs['validators'] = self.create_validators(prop, column)
        kwargs['filters'] = self.filters(column)
        kwargs.update(self.type_agnostic_parameters(prop.key, column))
        kwargs.update(self.type_specific_parameters(column))
        if prop.key in self.meta.field_args:
            kwargs.update(self.meta.field_args[prop.key])

        if issubclass(field_class, DecimalField):
            if hasattr(column.type, 'scale'):
                kwargs['places'] = column.type.scale
        field = field_class(**kwargs)
        return field

    def default(self, column):
        """
        Return field default for given column.

        :param column: SQLAlchemy Column object
        """
        if column.default and is_scalar(column.default.arg):
            return column.default.arg
        else:
            if not column.nullable:
                return self.meta.default

    def filters(self, column):
        """
        Return filters for given column.

        :param column: SQLAlchemy Column object
        """
        should_trim = column.info.get('trim', None)
        filters = column.info.get('filters', [])
        if (
            (
                isinstance(column.type, sa.types.String) and
                self.meta.strip_string_fields and
                should_trim is None
            ) or
            should_trim is True
        ):
            filters.append(strip_string)
        return filters

    def date_format(self, column):
        """
        Returns date format for given column.

        :param column: SQLAlchemy Column object
        """
        if (
            isinstance(column.type, sa.types.DateTime) or
            isinstance(column.type, types.ArrowType)
        ):
            return self.meta.datetime_format

        if isinstance(column.type, sa.types.Date):
            return self.meta.date_format

    def type_specific_parameters(self, column):
        """
        Returns type specific parameters for given column.

        :param column: SQLAlchemy Column object
        """
        kwargs = {}
        if (
            hasattr(column.type, 'enums') or
            column.info.get('choices') or
            isinstance(column.type, types.ChoiceType)
        ):
            kwargs.update(self.select_field_kwargs(column))

        date_format = self.date_format(column)
        if date_format:
            kwargs['format'] = date_format

        if hasattr(column.type, 'region'):
            kwargs['region'] = column.type.region

        kwargs['widget'] = self.widget(column)
        return kwargs

    def widget(self, column):
        """
        Returns WTForms widget for given column.

        :param column: SQLAlchemy Column object
        """
        widget = column.info.get('widget', None)
        if widget is not None:
            return widget

        kwargs = {}

        step = column.info.get('step', None)
        if step is not None:
            kwargs['step'] = step
        else:
            if isinstance(column.type, sa.types.Numeric):
                if (
                    column.type.scale is not None and
                    not column.info.get('choices')
                ):
                    kwargs['step'] = self.scale_to_step(column.type.scale)

        if kwargs:
            widget_class = self.WIDGET_MAP[
                self.get_field_class(column)
            ]
            return widget_class(**kwargs)

    def scale_to_step(self, scale):
        """
        Returns HTML5 compatible step attribute for given decimal scale.

        :param scale: an integer that defines a Numeric column's scale
        """
        return str(pow(Decimal('0.1'), scale))

    def type_agnostic_parameters(self, key, column):
        """
        Returns all type agnostic form field parameters for given column.

        :param column: SQLAlchemy Column object
        """
        kwargs = {}
        kwargs['description'] = column.info.get('description', '')
        kwargs['label'] = column.info.get('label', key)
        return kwargs

    def select_field_kwargs(self, column):
        """
        Returns key value args for SelectField based on SQLAlchemy column
        definitions.

        :param column: SQLAlchemy Column object
        """
        kwargs = {}
        kwargs['coerce'] = self.coerce(column)
        if isinstance(column.type, types.ChoiceType):
            kwargs['choices'] = column.type.choices
        elif 'choices' in column.info and column.info['choices']:
            kwargs['choices'] = column.info['choices']
        else:
            kwargs['choices'] = [
                (enum, enum) for enum in column.type.enums
            ]
        return kwargs

    def coerce(self, column):
        """
        Returns coerce callable for given column

        :param column: SQLAlchemy Column object
        """
        if 'coerce' in column.info:
            return column.info['coerce']
        if isinstance(column.type, types.ChoiceType):
            return choice_type_coerce_factory(column.type)
        try:
            python_type = column.type.python_type
        except NotImplementedError:
            return null_or_unicode

        if column.nullable and issubclass(python_type, six.string_types):
            return null_or_unicode
        return python_type

    def create_validators(self, prop, column):
        """
        Returns validators for given column

        :param column: SQLAlchemy Column object
        """
        validators = [
            self.required_validator(column),
            self.length_validator(column),
            self.unique_validator(prop.key, column),
            self.range_validator(column)
        ]
        if isinstance(column.type, types.EmailType):
            validators.append(self.get_validator('email'))
        if isinstance(column.type, types.URLType):
            validators.append(self.get_validator('url'))
        validators = flatten([v for v in validators if v is not None])

        validators.extend(self.additional_validators(prop.key, column))
        return validators

    def required_validator(self, column):
        """
        Returns required / optional validator for given column based on column
        nullability and form configuration.

        :param column: SQLAlchemy Column object
        """
        if (not self.meta.all_fields_optional and
                not column.default and
                not column.nullable):

            type_map = self.meta.not_null_validator_type_map
            try:
                return type_map[column.type]
            except KeyError:
                if isinstance(column.type, sa.types.TypeDecorator):
                    type_ = column.type.impl

                    try:
                        return type_map[type_]
                    except KeyError:
                        pass
                if self.meta.not_null_validator is not None:
                    return self.meta.not_null_validator
        return self.get_validator('optional')

    def get_validator(self, name, **kwargs):
        attr_name = '%s_validator' % name
        attr = getattr(self.meta, attr_name)
        if attr is None:
            return attr

        if inspect.ismethod(attr):
            return six.get_unbound_function(attr)(**kwargs)
        else:
            return attr(**kwargs)

    def additional_validators(self, key, column):
        """
        Returns additional validators for given column

        :param key: String key of the column property
        :param column: SQLAlchemy Column object
        """
        validators = []
        if key in self.meta.validators:
            try:
                validators.extend(self.meta.validators[key])
            except TypeError:
                validators.append(self.meta.validators[key])

        if 'validators' in column.info and column.info['validators']:
            try:
                validators.extend(column.info['validators'])
            except TypeError:
                validators.append(column.info['validators'])
        return validators

    def unique_validator(self, key, column):
        """
        Returns unique validator for given column if column has a unique index

        :param key: String key of the column property
        :param column: SQLAlchemy Column object
        """
        if column.unique:
            return self.get_validator(
                'unique',
                column=getattr(self.model_class, key),
                get_session=self.form_class.get_session
            )

    def range_validator(self, column):
        """
        Returns range validator based on column type and column info min and
        max arguments

        :param column: SQLAlchemy Column object
        """
        min_ = column.info.get('min')
        max_ = column.info.get('max')

        if min_ is not None or max_ is not None:
            if is_number(column.type) or is_number_range(column.type):
                return self.get_validator('number_range', min=min_, max=max_)
            elif is_date_column(column):
                return self.get_validator('date_range', min=min_, max=max_)
            elif isinstance(column.type, sa.types.Time):
                return self.get_validator('time_range', min=min_, max=max_)

    def length_validator(self, column):
        """
        Returns length validator for given column

        :param column: SQLAlchemy Column object
        """
        if (
            isinstance(column.type, sa.types.String) and
            hasattr(column.type, 'length') and
            column.type.length
        ):
            return self.get_validator('length', max=column.type.length)

    def get_field_class(self, column):
        """
        Returns WTForms field class. Class is based on a custom field class
        attribute or SQLAlchemy column type.

        :param column: SQLAlchemy Column object
        """
        if (
            'form_field_class' in column.info and
            column.info['form_field_class']
        ):
            return column.info['form_field_class']
        if 'choices' in column.info and column.info['choices']:
            return SelectField
        if (
            column.type not in self.TYPE_MAP and
            isinstance(column.type, sa.types.TypeDecorator)
        ):
            check_type = column.type.impl
        else:
            check_type = column.type

        try:
            column_type = self.TYPE_MAP[check_type]

            if inspect.isclass(column_type) and issubclass(column_type, Field):
                return column_type
            else:
                return column_type(column)
        except KeyError:
            raise UnknownTypeException(column)
