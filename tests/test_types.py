from enum import Enum

import sqlalchemy as sa
from pytest import mark, raises
from sqlalchemy_utils import (
    ChoiceType,
    ColorType,
    CountryType,
    EmailType,
    IntRangeType,
    PasswordType,
    PhoneNumberType,
    URLType,
    UUIDType,
)
from sqlalchemy_utils.types import arrow, phone_number, WeekDaysType  # noqa
from wtforms.fields import (
    BooleanField,
    FloatField,
    PasswordField,
    TextAreaField,
)
from wtforms.validators import Length, URL
from wtforms_components import Email
from wtforms_components.fields import (
    ColorField,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    IntegerField,
    IntIntervalField,
    SelectField,
    StringField,
    TimeField,
)

from tests import ModelFormTestCase
from wtforms_alchemy import (
    CountryField,
    ModelForm,
    null_or_unicode,
    PhoneNumberField,
    UnknownTypeException,
    WeekDaysField,
)
from wtforms_alchemy.utils import ClassMap

try:
    import passlib  # noqa
except ImportError:
    passlib = None


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

    def test_raises_exception_for_array_type(self):
        with raises(UnknownTypeException):
            self.init(type_=sa.ARRAY(sa.Integer))
            self.form_class()

    def test_unicode_converts_to_text_field(self):
        self.init()
        self.assert_type("test_column", StringField)

    def test_custom_unicode_converts_to_text_field(self):
        self.init(type_=CustomUnicodeType)
        self.assert_type("test_column", StringField)

    def test_string_converts_to_text_field(self):
        self.init(type_=sa.String)
        self.assert_type("test_column", StringField)

    def test_integer_converts_to_integer_field(self):
        self.init(type_=sa.Integer)
        self.assert_type("test_column", IntegerField)

    def test_unicode_text_converts_to_text_area_field(self):
        self.init(type_=sa.UnicodeText)
        self.assert_type("test_column", TextAreaField)

    def test_custom_unicode_text_converts_to_text_area_field(self):
        self.init(type_=CustomUnicodeTextType)
        self.assert_type("test_column", TextAreaField)

    def test_boolean_converts_to_boolean_field(self):
        self.init(type_=sa.Boolean)
        self.assert_type("test_column", BooleanField)

    def test_datetime_converts_to_datetime_field(self):
        self.init(type_=sa.DateTime)
        self.assert_type("test_column", DateTimeField)

    def test_date_converts_to_date_field(self):
        self.init(type_=sa.Date)
        self.assert_type("test_column", DateField)

    def test_float_converts_to_float_field(self):
        self.init(type_=sa.Float)
        self.assert_type("test_column", FloatField)

    def test_numeric_converts_to_decimal_field(self):
        self.init(type_=sa.Numeric)
        self.assert_type("test_column", DecimalField)

    def test_numeric_scale_converts_to_decimal_field_scale(self):
        self.init(type_=sa.Numeric(scale=4))
        form = self.form_class()
        assert form.test_column.places == 4

    def test_custom_numeric_converts_to_decimal_field(self):
        self.init(type_=CustomNumericType)
        self.assert_type("test_column", DecimalField)

    def test_enum_field_converts_to_select_field(self):
        choices = ["1", "2"]
        self.init(type_=sa.Enum(*choices))
        self.assert_type("test_column", SelectField)
        form = self.form_class()
        assert form.test_column.choices == [(s, s) for s in choices]

    def test_nullable_enum_uses_null_or_unicode_coerce_func_by_default(self):
        choices = ["1", "2"]
        self.init(type_=sa.Enum(*choices), nullable=True)
        field = self._get_field("test_column")
        assert field.coerce == null_or_unicode

    def test_custom_choices_override_enum_choices(self):
        choices = ["1", "2"]
        custom_choices = [("2", "2"), ("3", "3")]
        self.init(type_=sa.Enum(*choices), info={"choices": custom_choices})
        form = self.form_class()
        assert form.test_column.choices == custom_choices

    def test_column_with_choices_converts_to_select_field(self):
        choices = [("1", "1"), ("2", "2")]
        self.init(type_=sa.Integer, info={"choices": choices})
        self.assert_type("test_column", SelectField)
        form = self.form_class()
        assert form.test_column.choices == choices

    def test_assigns_email_validator_for_email_type(self):
        self.init(type_=EmailType)
        self.assert_has_validator("test_column", Email)

    def test_assigns_url_validator_for_url_type(self):
        self.init(type_=URLType)
        self.assert_has_validator("test_column", URL)

    def test_time_converts_to_time_field(self):
        self.init(type_=sa.types.Time)
        self.assert_type("test_column", TimeField)

    def test_varchar_converts_to_text_field(self):
        self.init(type_=sa.types.VARCHAR)
        self.assert_type("test_column", StringField)

    def test_text_converts_to_textarea_field(self):
        self.init(type_=sa.types.TEXT)
        self.assert_type("test_column", TextAreaField)

    def test_char_converts_to_text_field(self):
        self.init(type_=sa.types.CHAR)
        self.assert_type("test_column", StringField)

    def test_real_converts_to_float_field(self):
        self.init(type_=sa.types.REAL)
        self.assert_type("test_column", FloatField)

    def test_json_converts_to_textarea_field(self):
        self.init(type_=sa.types.JSON)
        self.assert_type("test_column", TextAreaField)

    @mark.xfail("phone_number.phonenumbers is None")
    def test_phone_number_converts_to_phone_number_field(self):
        self.init(type_=PhoneNumberType)
        self.assert_type("test_column", PhoneNumberField)

    @mark.xfail("phone_number.phonenumbers is None")
    def test_phone_number_country_code_passed_to_field(self):
        self.init(type_=PhoneNumberType(region="SE"))
        form = self.form_class()
        assert form.test_column.region == "SE"

    @mark.xfail("phone_number.phonenumbers is None")
    def test_phone_number_type_has_no_length_validation(self):
        self.init(type_=PhoneNumberType(country_code="FI"))
        field = self._get_field("test_column")
        for validator in field.validators:
            assert validator.__class__ != Length

    @mark.parametrize(("type", "field"), ((IntRangeType, IntIntervalField),))
    def test_range_type_conversion(self, type, field):
        self.init(type_=type)
        self.assert_type("test_column", field)

    @mark.xfail("passlib is None")
    def test_password_type_converts_to_password_field(self):
        self.init(type_=PasswordType)
        self.assert_type("test_column", PasswordField)

    @mark.xfail("arrow.arrow is None")
    def test_arrow_type_converts_to_datetime_field(self):
        self.init(type_=arrow.ArrowType)
        self.assert_type("test_column", DateTimeField)

    def test_url_type_converts_to_string_field(self):
        self.init(type_=URLType)
        self.assert_type("test_column", StringField)

    def test_uuid_type_converst_to_uuid_type(self):
        self.init(type_=UUIDType)
        self.assert_type("test_column", StringField)

    def test_color_type_converts_to_color_field(self):
        self.init(type_=ColorType)
        self.assert_type("test_column", ColorField)

    def test_email_type_converts_to_email_field(self):
        self.init(type_=EmailType)
        self.assert_type("test_column", EmailField)

    def test_country_type_converts_to_country_field(self):
        self.init(type_=CountryType)
        self.assert_type("test_column", CountryField)

    def test_choice_type_converts_to_select_field(self):
        choices = [("1", "choice 1"), ("2", "choice 2")]
        self.init(type_=ChoiceType(choices))
        self.assert_type("test_column", SelectField)
        assert list(self.form_class().test_column.choices) == choices

    def test_choice_type_uses_custom_coerce_func(self):
        choices = [("1", "choice 1"), ("2", "choice 2")]
        self.init(type_=ChoiceType(choices))
        self.assert_type("test_column", SelectField)
        model = self.ModelTest(test_column="2")
        form = self.form_class(obj=model)
        assert '<option selected value="2">' in str(form.test_column)

    def test_choice_type_with_enum(self):
        class Choice(Enum):
            choice1 = 1
            choice2 = 2

            def __str__(self):
                return self.name

        self.init(type_=ChoiceType(Choice))
        self.assert_type("test_column", SelectField)
        assert self.form_class().test_column.choices == [(1, "choice1"), (2, "choice2")]

    @mark.parametrize(["type_", "impl"], [(int, sa.Integer()), (str, sa.String())])
    def test_choice_type_with_enum_uses_custom_coerce_func(self, type_, impl):
        class Choice(Enum):
            choice1 = type_(1)
            choice2 = type_(2)

            def __str__(self):
                return self.name

        self.init(type_=ChoiceType(Choice, impl=impl))
        self.assert_type("test_column", SelectField)
        model = self.ModelTest(test_column=type_(2))
        form = self.form_class(obj=model)
        assert '<option selected value="2">' in str(form.test_column)


class TestWeekDaysTypeConversion(ModelFormTestCase):
    def test_weekdays_type_converts_to_weekdays_field(self):
        self.init(type_=WeekDaysType)
        self.assert_type("test_column", WeekDaysField)


class TestCustomTypeMap(ModelFormTestCase):
    def test_override_type_map_on_class_level(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Unicode(255), nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_validator = None
                type_map = ClassMap({sa.Unicode: TextAreaField})

        form = ModelTestForm()
        assert isinstance(form.test_column, TextAreaField)

    def test_override_type_map_with_callable(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column_short = sa.Column(sa.Unicode(255), nullable=False)
            test_column_long = sa.Column(sa.Unicode(), nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_validator = None
                type_map = ClassMap(
                    {
                        sa.Unicode: lambda column: (
                            StringField if column.type.length else TextAreaField
                        )
                    }
                )

        form = ModelTestForm()
        assert isinstance(form.test_column_short, StringField)
        assert isinstance(form.test_column_long, TextAreaField)
