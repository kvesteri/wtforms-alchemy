#import pytz
from collections import OrderedDict
from decimal import Decimal
from wtforms import (
    BooleanField,
    FloatField,
    TextAreaField,
    PasswordField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
)
import sqlalchemy as sa
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy_utils import types
from wtforms_components import (
    ColorField,
    DateField,
    DateRange,
    DateTimeField,
    DecimalField,
    Email,
    EmailField,
    IntegerField,
    NumberRangeField,
    PhoneNumberField,
    SelectField,
    StringField,
    TimeField,
    TimeRange,
    Unique,
)
from wtforms_components.widgets import NumberInput
from .exc import InvalidAttributeException, UnknownTypeException
from .utils import (
    is_date_column,
    is_integer_column,
    is_scalar,
    null_or_unicode,
    trim,
)


class FormGenerator(object):
    """
    Base form generator, you can make your own form generators by inheriting
    this class.
    """

    # When converting SQLAlchemy types to fields this ordered dict is iterated
    # in given order. This allows smart type conversion of different inherited
    # type objects.
    TYPE_MAP = OrderedDict((
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
        (sa.types.String, StringField),
        (sa.types.Time, TimeField),
        (sa.types.Unicode, StringField),
        (types.ArrowType, DateTimeField),
        (types.ColorType, ColorField),
        (types.EmailType, EmailField),
        (types.NumberRangeType, NumberRangeField),
        (types.PasswordType, PasswordField),
        (types.PhoneNumberType, PhoneNumberField),
        (types.ScalarListType, StringField),
        (types.UUIDType, StringField),
    ))

    WIDGET_MAP = OrderedDict((
        (DecimalField, NumberInput),
        (FloatField, NumberInput),
        (IntegerField, NumberInput),
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

    def create_form(self, form):
        """
        Creates the form.

        :param form: ModelForm instance
        """
        attrs = set(self.model_class._sa_class_manager.values())
        tmp = []
        for attr in attrs:
            property_ = attr.property
            if not isinstance(property_, ColumnProperty):
                continue
            if self.skip_column_property(property_):
                continue
            tmp.append(attr)
        tmp += self.translated_attributes
        attrs = set(tmp)

        return self.create_fields(form, self.filter_attributes(attrs))

    def filter_attributes(self, attrs):
        """
        Filter set of model attributes based on only, exclude and include
        meta parameters.

        :param attrs: Set of attributes
        """
        if self.meta.only:
            attrs = set(map(self.validate_attribute, self.meta.only))
        else:
            if self.meta.include:
                attrs.update(map(self.validate_attribute, self.meta.include))

            if self.meta.exclude:
                func = lambda a: a.key not in self.meta.exclude
                attrs = filter(func, attrs)
        return attrs

    def validate_attribute(self, attr_name):
        """
        Finds out whether or not given sqlalchemy model attribute name is
        valid.

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
                raise InvalidAttributeException(attr_name)

        try:
            if not isinstance(attr.property, ColumnProperty):
                raise InvalidAttributeException(attr_name)
        except AttributeError:
            raise InvalidAttributeException(attr_name)
        return attr

    @property
    def translated_attributes(self):
        """
        Return translated attributes for current model class. See
        `SQLAlchemy-i18n package`_ for more information about translatable
        attributes.

        .. _`SQLAlchemy-i18n package`:
            https://github.com/kvesteri/sqlalchemy-i18n
        """
        try:
            columns = self.model_class.__translated_columns__
        except AttributeError:
            return []
        else:
            translation_class = self.model_class.__translatable__['class']
            return [
                getattr(translation_class, column.name)
                for column in columns
            ]

    def create_fields(self, form, attributes):
        """
        Creates fields for given form based on given model attributes.

        :param form: form to attach the generated fields into
        :param attributes: model attributes to generate the form fields from
        """
        for attribute in attributes:
            column_property = attribute.property
            column = column_property.columns[0]
            form_field = self.create_field(column)

            if not hasattr(form, column.name):
                setattr(form, column.name, form_field)

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
        if (not self.meta.include_primary_keys and column.primary_key or
                column.foreign_keys):
            return True

        if (not self.meta.include_datetimes_with_default and
                isinstance(column.type, sa.types.DateTime) and
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

    def create_field(self, column):
        """
        Create form field for given column.

        :param column: SQLAlchemy Column object.
        """
        kwargs = {}
        field_class = self.get_field_class(column)
        kwargs['default'] = self.default(column)
        kwargs['validators'] = self.create_validators(column)
        kwargs.update(self.type_agnostic_parameters(column))
        kwargs.update(self.type_specific_parameters(column))
        kwargs.setdefault('filters', [])
        kwargs['filters'] += self.filters(column)
        return field_class(**kwargs)

    def format(self, column):
        """
        Return field format for given column.

        :param column: SQLAlchemy Column object
        """
        if isinstance(column.type, sa.types.DateTime):
            return self.meta.datetime_format

        if isinstance(column.type, sa.types.Date):
            return self.meta.date_format

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
            ) or should_trim is True
        ):
            filters.append(trim)
        return filters

    def type_specific_parameters(self, column):
        """
        Returns type specific parameters for given column.

        :param column: SQLAlchemy Column object
        """
        kwargs = {}
        if (hasattr(column.type, 'enums') or column.info.get('choices')):
            kwargs.update(self.select_field_kwargs(column))

        if isinstance(column.type, sa.types.DateTime):
            kwargs['format'] = self.meta.datetime_format

        if isinstance(column.type, sa.types.Date):
            kwargs['format'] = self.meta.date_format

        if hasattr(column.type, 'country_code'):
            kwargs['country_code'] = column.type.country_code

        kwargs['widget'] = self.widget(column)
        return kwargs

    def widget(self, column):
        widget = column.info.get('widget', None)
        if widget is not None:
            return widget

        kwargs = {}

        step = column.info.get('step', None)
        if step is not None:
            kwargs['step'] = step
        else:
            if isinstance(column.type, sa.types.Numeric):
                if column.type.scale is not None:
                    kwargs['step'] = self.scale_to_step(column.type.scale)

        if kwargs:
            widget_class = self.WIDGET_MAP[
                self.get_field_class(column)
            ]
            return widget_class(**kwargs)

    def scale_to_step(self, scale):
        return str(pow(Decimal('0.1'), scale))

    def type_agnostic_parameters(self, column):
        """
        Returns all type agnostic form field parameters for given column.

        :param column: SQLAlchemy Column object
        """
        name = column.name
        kwargs = {}
        kwargs['description'] = column.info.get('description', '')
        kwargs['label'] = column.info.get('label', name)
        return kwargs

    def select_field_kwargs(self, column):
        """
        Returns key value args for SelectField based on SQLAlchemy column
        definitions.

        :param column: SQLAlchemy Column object
        """
        kwargs = {}
        try:
            kwargs['coerce'] = column.type.python_type
        except NotImplementedError:
            kwargs['coerce'] = null_or_unicode
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
        Returns validators for given column

        :param column: SQLAlchemy Column object
        """
        validators = [
            self.required_validator(column),
            self.length_validator(column),
            self.unique_validator(column),
            self.range_validator(column)
        ]
        validators = [v for v in validators if v is not None]
        if isinstance(column.type, types.EmailType):
            validators.append(Email())
        validators.extend(self.additional_validators(column))
        return validators

    def required_validator(self, column):
        """
        Returns required / optional validator for given column based on column
        nullability and form configuration.

        :param column: SQLAlchemy Column object
        """
        if (not self.meta.all_fields_optional and
                not column.default and
                not column.nullable and
                self.meta.assign_required):
            return DataRequired()
        return Optional()

    def additional_validators(self, column):
        """
        Returns additional validators for given column

        :param column: SQLAlchemy Column object
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

        :param column: SQLAlchemy Column object
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

        :param column: SQLAlchemy Column object
        """
        min_ = column.info.get('min', None)
        max_ = column.info.get('max', None)

        if min_ is not None or max_ is not None:
            if is_integer_column(column):
                return NumberRange(min=min_, max=max_)
            elif is_date_column(column):
                return DateRange(min=min_, max=max_)
            elif isinstance(column.type, sa.types.Time):
                return TimeRange(min=min_, max=max_)

    def length_validator(self, column):
        """
        Returns length validator for given column

        :param column: SQLAlchemy Column object
        """
        if isinstance(column.type, types.PhoneNumberType):
            return
        if hasattr(column.type, 'length') and column.type.length:
            return Length(max=column.type.length)

    def get_field_class(self, column):
        """
        Returns WTForms field class. Class is based on a custom field class
        attribute or SQLAlchemy column type.

        :param column: SQLAlchemy Column object
        """
        if ('form_field_class' in column.info
                and column.info['form_field_class']):
            return column.info['form_field_class']
        if 'choices' in column.info and column.info['choices']:
            return SelectField
        if (
            type(column.type) not in self.TYPE_MAP and
            isinstance(column.type, sa.types.TypeDecorator)
        ):
            check_type = column.type.impl
        else:
            check_type = column.type
        for type_ in self.TYPE_MAP:
            if isinstance(check_type, type_):
                return self.TYPE_MAP[type_]
        raise UnknownTypeException(column)
