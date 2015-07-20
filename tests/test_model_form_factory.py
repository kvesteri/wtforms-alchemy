from distutils.version import LooseVersion

import wtforms
from pytest import raises
from wtforms import Form

from tests import ModelFormTestCase
from wtforms_alchemy import (
    FormGenerator,
    model_form_factory,
    UnknownConfigurationOption
)


class TestModelFormFactory(ModelFormTestCase):
    def test_supports_parameter_overriding(self):
        self.init()

        class MyFormGenerator(FormGenerator):
            pass

        defaults = {
            'all_fields_optional': True,
            'only_indexed_fields': True,
            'include_primary_keys': True,
            'include_foreign_keys': True,
            'strip_string_fields': True,
            'include_datetimes_with_default': True,
            'form_generator': True,
            'date_format': '%d-%m-%Y',
            'datetime_format': '%Y-%m-%dT%H:%M:%S',
        }
        ModelForm = model_form_factory(Form, **defaults)
        for key, value in defaults.items():
            assert getattr(ModelForm.Meta, key) == value

    def test_throws_exception_for_unknown_configuration_option(self):
        self.init()

        class SomeForm(Form):
            pass

        defaults = {
            'unknown': 'something'
        }
        with raises(UnknownConfigurationOption):
            model_form_factory(SomeForm, **defaults)

    def test_supports_custom_base_class_with_model_form_factory(self):
        self.init()

        class SomeForm(Form):
            pass

        class TestCustomBase(model_form_factory(SomeForm)):
            class Meta:
                model = self.ModelTest

        assert isinstance(TestCustomBase(), SomeForm)

    def test_url_validator(self):
        form = model_form_factory(url_validator=None)
        assert form.Meta.url_validator is None

    def test_email_validator(self):
        form = model_form_factory(email_validator=None)
        assert form.Meta.email_validator is None

    def test_length_validator(self):
        form = model_form_factory(length_validator=None)
        assert form.Meta.length_validator is None

    def test_number_range_validator(self):
        form = model_form_factory(number_range_validator=None)
        assert form.Meta.number_range_validator is None

    def test_date_range_validator(self):
        form = model_form_factory(date_range_validator=None)
        assert form.Meta.date_range_validator is None

    def test_time_range_validator(self):
        form = model_form_factory(time_range_validator=None)
        assert form.Meta.time_range_validator is None

    def test_optional_validator(self):
        form = model_form_factory(optional_validator=None)
        assert form.Meta.optional_validator is None

    def test_unique_validator(self):
        form = model_form_factory(unique_validator=None)
        assert form.Meta.unique_validator is None

    def test_class_meta_wtforms2(self):
        if LooseVersion(wtforms.__version__) < LooseVersion('2'):
            return  # skip test for wtforms < 2

        self.init()

        class SomeForm(Form):
            class Meta:
                locales = ['fr']
                foo = 9

        class OtherForm(SomeForm):
            class Meta:
                pass

        class TestCustomBase(model_form_factory(SomeForm)):
            class Meta:
                model = self.ModelTest

        form = TestCustomBase()
        other_form = OtherForm()
        assert isinstance(form.meta, wtforms.meta.DefaultMeta)
        assert form.meta.locales == ['fr']
        assert hasattr(form.meta, 'model')
        assert hasattr(form.meta, 'csrf')

        assert form.meta.foo == 9
        # Create a side effect on the base meta.
        SomeForm.Meta.foo = 12
        assert other_form.meta.foo == 12
        assert form.meta.foo == 12
