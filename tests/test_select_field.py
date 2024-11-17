from decimal import Decimal

import six
import sqlalchemy as sa
from wtforms_components import SelectField

from tests import ModelFormTestCase


class MultiDict(dict):
    def getlist(self, key):
        return [self[key]]


class TestSelectFieldDefaultValue(ModelFormTestCase):
    def test_option_selected_by_field_default_value(self):
        choices = [("1", "1"), ("2", "2")]
        self.init(type_=sa.Integer, default="1", info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": "2"}))
        assert '<option selected value="2">2</option>' in str(form.test_column)


class TestSelectFieldCoerce(ModelFormTestCase):
    def test_integer_coerces_values_to_integers(self):
        choices = [("1", "1"), ("2", "2")]
        self.init(type_=sa.Integer, info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": "2"}))
        assert form.test_column.data == 2

    def test_nullable_integer_coerces_values_to_integers(self):
        choices = [("1", "1"), ("2", "2")]
        self.init(type_=sa.Integer, nullable=True, info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": "2"}))
        assert form.test_column.data == 2

    def test_integer_coerces_empty_strings_to_nulls(self):
        choices = [("1", "1"), ("2", "2")]
        self.init(type_=sa.Integer, info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": ""}))
        assert form.test_column.data is None

    def test_big_integer_coerces_values_to_integers(self):
        choices = [("1", "1"), ("2", "2")]
        self.init(type_=sa.BigInteger, info={"choices": choices})
        self.assert_type("test_column", SelectField)
        form = self.form_class(MultiDict({"test_column": "2"}))
        assert form.test_column.data == 2

    def test_small_integer_coerces_values_to_integers(self):
        choices = [("1", "1"), ("2", "2")]
        self.init(type_=sa.SmallInteger, info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": "2"}))
        assert form.test_column.data == 2

    def test_numeric_coerces_values_to_decimals(self):
        choices = [("1.0", "1.0"), ("2.0", "2.0")]
        self.init(type_=sa.Numeric, info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": "2.0"}))
        assert form.test_column.data == Decimal("2.0")

    def test_float_coerces_values_to_floats(self):
        choices = [("1.0", "1.0"), ("2.0", "2.0")]
        self.init(type_=sa.Float, info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": "2.0"}))
        assert form.test_column.data == 2.0

    def test_unicode_coerces_values_to_unicode_strings(self):
        choices = [("1.0", "1.0"), ("2.0", "2.0")]
        self.init(type_=sa.Unicode(255), info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": "2.0"}))
        assert form.test_column.data == "2.0"
        assert isinstance(form.test_column.data, six.text_type)

    def test_unicode_text_coerces_values_to_unicode_strings(self):
        choices = [("1.0", "1.0"), ("2.0", "2.0")]
        self.init(type_=sa.UnicodeText, info={"choices": choices})
        form = self.form_class(MultiDict({"test_column": "2.0"}))
        assert form.test_column.data == "2.0"
        assert isinstance(form.test_column.data, six.text_type)
