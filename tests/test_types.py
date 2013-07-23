from pytest import raises
import sqlalchemy as sa
from wtforms.fields import (
    TextField,
    TextAreaField,
    BooleanField,
    FloatField,
)
from wtforms.validators import Length
from sqlalchemy_utils import (
    ColorType,
    PhoneNumberType,
    NumberRangeType,
    EmailType
)
from wtforms_components import (
    ColorField,
    DateField,
    DateTimeField,
    DecimalField,
    Email,
    EmailField,
    IntegerField,
    NumberRangeField,
    TimeField,
)
from wtforms_alchemy import (
    SelectField,
    UnknownTypeException,
    null_or_unicode
)
from wtforms_components import PhoneNumberField
from tests import ModelFormTestCase


class UnknownType(sa.types.UserDefinedType):

    def get_col_spec(self):
        return "UNKNOWN()"

class CustomUnicodeTextType(sa.types.TypeDecorator):
    impl = sa.types.UnicodeText


class CustomUnicodeType(sa.types.TypeDecorator):
    impl = sa.types.Unicode


class CustomNumericType(sa.types.TypeDecorator):
    impl = sa.types.Numeric


class TestModelColumnToFormFieldTypeConversion(ModelFormTestCase):
    def test_raises_exception_for_unknown_type(self):
        with raises(UnknownTypeException):
            self.init(type_=UnknownType)
            self.form_class()

    def test_unicode_converts_to_text_field(self):
        self.init()
        self.assert_type('test_column', TextField)

    def test_custom_unicode_converts_to_text_field(self):
        self.init(type_=CustomUnicodeType)
        self.assert_type('test_column', TextField)

    def test_string_converts_to_text_field(self):
        self.init(type_=sa.String)
        self.assert_type('test_column', TextField)

    def test_integer_converts_to_integer_field(self):
        self.init(type_=sa.Integer)
        self.assert_type('test_column', IntegerField)

    def test_unicode_text_converts_to_text_area_field(self):
        self.init(type_=sa.UnicodeText)
        self.assert_type('test_column', TextAreaField)

    def test_custom_unicode_text_converts_to_text_area_field(self):
        self.init(type_=CustomUnicodeTextType)
        self.assert_type('test_column', TextAreaField)

    def test_boolean_converts_to_boolean_field(self):
        self.init(type_=sa.Boolean)
        self.assert_type('test_column', BooleanField)

    def test_datetime_converts_to_datetime_field(self):
        self.init(type_=sa.DateTime)
        self.assert_type('test_column', DateTimeField)

    def test_date_converts_to_date_field(self):
        self.init(type_=sa.Date)
        self.assert_type('test_column', DateField)

    def test_float_converts_to_float_field(self):
        self.init(type_=sa.Float)
        self.assert_type('test_column', FloatField)

    def test_numeric_converts_to_decimal_field(self):
        self.init(type_=sa.Numeric)
        self.assert_type('test_column', DecimalField)

    def test_custom_numeric_converts_to_decimal_field(self):
        self.init(type_=CustomNumericType)
        self.assert_type('test_column', DecimalField)

    def test_enum_field_converts_to_select_field(self):
        choices = ['1', '2']
        self.init(type_=sa.Enum(*choices))
        self.assert_type('test_column', SelectField)
        form = self.form_class()
        assert form.test_column.choices == [(s, s) for s in choices]

    def test_nullable_enum_uses_null_or_unicode_coerce_func_by_default(self):
        choices = ['1', '2']
        self.init(type_=sa.Enum(*choices), nullable=True)
        field = self._get_field('test_column')
        assert field.coerce == null_or_unicode

    def test_custom_choices_override_enum_choices(self):
        choices = ['1', '2']
        custom_choices = [('2', '2'), ('3', '3')]
        self.init(type_=sa.Enum(*choices), info={'choices': custom_choices})
        form = self.form_class()
        assert form.test_column.choices == custom_choices

    def test_column_with_choices_converts_to_select_field(self):
        choices = [(u'1', '1'), (u'2', '2')]
        self.init(type_=sa.Integer, info={'choices': choices})
        self.assert_type('test_column', SelectField)
        form = self.form_class()
        assert form.test_column.choices == choices

    def test_assigns_email_validator_for_email_type(self):
        self.init(type_=EmailType)
        self.assert_has_validator('test_column', Email)

    def test_time_converts_to_time_field(self):
        self.init(type_=sa.types.Time)
        self.assert_type('test_column', TimeField)

    def test_varchar_converts_to_text_field(self):
        self.init(type_=sa.types.VARCHAR)
        self.assert_type('test_column', TextField)

    def test_text_converts_to_textarea_field(self):
        self.init(type_=sa.types.TEXT)
        self.assert_type('test_column', TextAreaField)

    def test_char_converts_to_text_field(self):
        self.init(type_=sa.types.CHAR)
        self.assert_type('test_column', TextField)

    def test_real_converts_to_float_field(self):
        self.init(type_=sa.types.REAL)
        self.assert_type('test_column', FloatField)

    def test_phone_number_converts_to_phone_number_field(self):
        self.init(type_=PhoneNumberType)
        self.assert_type('test_column', PhoneNumberField)

    def test_phone_number_country_code_passed_to_field(self):
        self.init(type_=PhoneNumberType(country_code='SE'))
        form = self.form_class()
        assert form.test_column.country_code == 'SE'

    def test_phone_number_type_has_no_length_validation(self):
        self.init(type_=PhoneNumberType(country_code='FI'))
        field = self._get_field('test_column')
        for validator in field.validators:
            assert validator.__class__ != Length

    def test_number_range_converts_to_number_range_field(self):
        self.init(type_=NumberRangeType)
        self.assert_type('test_column', NumberRangeField)

    def test_color_type_converts_to_color_field(self):
        self.init(type_=ColorType)
        self.assert_type('test_column', ColorField)

    def test_email_type_converts_to_email_field(self):
        self.init(type_=EmailType)
        self.assert_type('test_column', EmailField)
