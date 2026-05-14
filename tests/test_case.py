from wtforms import Field
from wtforms.validators import DataRequired, Length, Optional


class FormTestCase:
    form_class = None

    def _make_form(self, *args, **kwargs):
        return self.form_class(csrf_enabled=False, *args, **kwargs)

    def _get_field(self, field_name):
        form = self._make_form()
        return getattr(form, field_name)

    def _get_validator(self, field, validator_class):
        for validator in field.validators:
            if isinstance(validator, validator_class):
                return validator

    def get_validator(self, field_name, validator_class):
        return self._get_validator(self._get_field(field_name), validator_class)

    def has_field(self, field_name):
        form = self._make_form()
        return hasattr(form, field_name)

    def assert_type(self, field_name, field_type):
        self.assert_has(field_name)
        assert self._get_field(field_name).__class__ is field_type

    def assert_has(self, field_name):
        try:
            field = self._get_field(field_name)
        except AttributeError:
            field = None
        msg = f"Form does not have a field called '{field_name}'."
        assert isinstance(field, Field), msg

    def assert_max_length(self, field_name, max_length):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple Length validators
            if isinstance(validator, Length):
                if validator.max == max_length:
                    found = True
        assert found, "Field does not have max length of %d" % max_length

    def assert_description(self, field_name, description):
        field = self._get_field(field_name)
        assert field.description == description

    def assert_default(self, field_name, default):
        field = self._get_field(field_name)
        assert field.default == default

    def assert_label(self, field_name, label):
        field = self._get_field(field_name)
        assert field.label.text == label

    def assert_has_validator(self, field_name, validator):
        field = self._get_field(field_name)
        msg = f"Field '{field_name}' does not have validator {validator!r}."
        assert self._get_validator(field, validator), msg

    def assert_optional(self, field_name):
        field = self._get_field(field_name)
        msg = f"Field '{field_name}' is not optional."
        assert self._get_validator(field, Optional), msg

    def assert_not_required(self, field_name):
        field = self._get_field(field_name)
        msg = f"Field '{field_name}' is required."
        assert not self._get_validator(field, DataRequired), msg
