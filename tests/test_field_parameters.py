from datetime import date, time
import sqlalchemy as sa
from wtforms import widgets
from wtforms_alchemy import ModelForm
from wtforms_components import DateRange, TimeRange
from wtforms.fields import StringField
from wtforms.validators import NumberRange
from tests import ModelFormTestCase


class TestFieldParameters(ModelFormTestCase):
    def test_accepts_custom_widgets(self):
        self.init(info={'widget': widgets.HiddenInput()})
        form = self.form_class()
        assert isinstance(form.test_column.widget, widgets.HiddenInput)

    def test_accepts_custom_filters(self):
        test_filter = lambda a: a
        self.init(info={'filters': [test_filter]})
        form = self.form_class()
        assert test_filter in form.test_column.filters

    def test_assigns_description_from_column_info(self):
        self.init(info={'description': 'Description'})
        self.assert_description('test_column', 'Description')

    def test_does_not_add_default_value_if_default_is_callable(self):
        self.init(default=lambda: "test")
        self.assert_default('test_column', None)

    def test_assigns_scalar_defaults(self):
        self.init(default=u"test")
        self.assert_default('test_column', "test")

    def test_min_and_max_info_attributes_generate_number_range_validator(self):
        self.init(type_=sa.Integer, info={'min': 1, 'max': 100})
        validator = self.get_validator('test_column', NumberRange)
        assert validator.min == 1
        assert validator.max == 100

    def test_min_and_max_info_attributes_generate_time_range_validator(self):
        self.init(
            type_=sa.types.Time,
            info={'min': time(12, 30), 'max': time(14, 30)}
        )
        validator = self.get_validator('test_column', TimeRange)
        assert validator.min == time(12, 30)
        assert validator.max == time(14, 30)

    def test_min_and_max_info_attributes_generate_date_range_validator(self):
        self.init(
            type_=sa.Date,
            info={'min': date(1990, 1, 1), 'max': date(2000, 1, 1)}
        )
        validator = self.get_validator('test_column', DateRange)
        assert validator.min == date(1990, 1, 1)
        assert validator.max == date(2000, 1, 1)

    def test_uses_custom_field_class(self):
        class InputTest(widgets.Input):
            input_type = 'color'

        class FieldTest(StringField):
            widget = InputTest()

        class ModelTest(self.base):
            __tablename__ = 'model_test'
            query = None
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(
                sa.UnicodeText,
                info={'form_field_class': FieldTest}
            )

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest

        form = ModelTestForm()
        assert 'type="color"' in str(form.test_column)

    def test_accepts_none_as_custom_field_class(self):
        class InputTest(widgets.Input):
            input_type = 'color'

        class FieldTest(StringField):
            widget = InputTest()

        class ModelTest(self.base):
            __tablename__ = 'model_test'
            query = None
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(
                sa.UnicodeText,
                info={'form_field_class': None}
            )

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest

        assert ModelTestForm()
