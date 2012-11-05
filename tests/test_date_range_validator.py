from datetime import date
from wtforms_alchemy import DateRange
from wtforms_test import FormTestCase
from wtforms import Form
from wtforms.fields import DateField
from tests import MultiDict


class TestDateRangeValidator(FormTestCase):
    def init_form(self, **kwargs):
        class ModelTestForm(Form):
            date = DateField(validators=[DateRange(**kwargs)])

        self.form_class = ModelTestForm
        return self.form_class

    def test_date_greater_than_validator(self):
        form_class = self.init_form(min=date(1990, 1, 1))
        form = form_class(MultiDict(date='1980-1-1'))
        form.validate()
        error_msg = u'Date must be greater than 1990-01-01.'
        assert form.errors['date'] == [error_msg]

    def test_date_less_than_validator(self):
        form_class = self.init_form(max=date(1990, 1, 1))
        form = form_class(MultiDict(date='1991-1-1'))
        form.validate()
        error_msg = u'Date must be less than 1990-01-01.'
        assert form.errors['date'] == [error_msg]

    def test_date_between_validator(self):
        form_class = self.init_form(min=date(1990, 1, 1), max=date(1991, 1, 1))
        form = form_class(MultiDict(date='1989-1-1'))
        form.validate()
        error_msg = u'Date must be between 1990-01-01 and 1991-01-01.'
        assert form.errors['date'] == [error_msg]
