import sqlalchemy_utils
from babel import Locale
from wtforms import Form

from tests import MultiDict
from wtforms_alchemy import CountryField

sqlalchemy_utils.i18n.get_locale = lambda: Locale('en')


class TestCountryField(object):
    field_class = CountryField

    def init_form(self, **kwargs):
        class TestForm(Form):
            test_field = self.field_class(**kwargs)

        self.form_class = TestForm
        return self.form_class

    def setup_method(self, method):
        self.valid_countries = [
            'US',
            'SA',
            'FI'
        ]
        self.invalid_countries = [
            'unknown',
        ]

    def test_valid_countries(self):
        form_class = self.init_form()
        for country in self.valid_countries:
            form = form_class(MultiDict(test_field=country))
            form.validate()
            assert len(form.errors) == 0

    def test_invalid_countries(self):
        form_class = self.init_form()
        for country in self.invalid_countries:
            form = form_class(MultiDict(test_field=country))
            form.validate()
            assert len(form.errors['test_field']) == 2
