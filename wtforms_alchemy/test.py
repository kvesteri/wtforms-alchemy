from wtforms import Field

from wtforms.validators import Required, Length, Email, Optional, NumberRange
from . import Unique


class FormTestCase(object):
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
        return self._get_validator(
            self._get_field(field_name),
            validator_class
        )

    def has_field(self, field_name):
        form = self._make_form()
        return hasattr(form, field_name)

    def assert_field_type(self, field_name, field_type):
        self.assert_has_field(field_name)
        assert self._get_field(field_name).__class__ is field_type

    def assert_has_field(self, field_name):
        try:
            field = self._get_field(field_name)
        except AttributeError:
            field = None
        msg = "Form does not have a field called '%s'." % field_name
        assert isinstance(field, Field), msg

    def assert_field_min_value(self, field_name, min_value):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple NumberRange validators
            if isinstance(validator, NumberRange):
                if validator.min == min_value:
                    found = True
        assert found, "Field does not have min value of %d" % min_value

    def assert_field_max_value(self, field_name, max_value):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple NumberRange validators
            if isinstance(validator, NumberRange):
                if validator.max == max_value:
                    found = True
        assert found, "Field does not have max value of %d" % max_value

    def assert_field_min_length(self, field_name, min_length):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple Length validators
            if isinstance(validator, Length):
                if validator.min == min_length:
                    found = True
        assert found, "Field does not have min length of %d" % min_length

    def assert_field_max_length(self, field_name, max_length):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple Length validators
            if isinstance(validator, Length):
                if validator.max == max_length:
                    found = True
        assert found, "Field does not have max length of %d" % max_length

    def assert_field_default(self, field_name, default):
        field = self._get_field(field_name)
        assert field.default == default

    def assert_field_label(self, field_name, label):
        field = self._get_field(field_name)
        assert field.label.text == label

    def assert_field_is_unique(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' not is unique." % field_name
        assert self._get_validator(field, Unique), msg

    def assert_field_is_not_optional(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is optional." % field_name
        assert not self._get_validator(field, Required), msg

    def assert_field_is_optional(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is not optional." % field_name
        assert self._get_validator(field, Optional), msg

    def assert_field_is_not_required(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is required." % field_name
        assert not self._get_validator(field, Required), msg

    def assert_field_is_required(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is not required." % field_name
        assert self._get_validator(field, Required), msg

    def assert_field_must_be_valid_email_address(self, field_name):
        field = self._get_field(field_name)
        msg = (
            "Field '%s' is not required to be a valid email address." %
            field_name
        )
        assert self._get_validator(field, Email), msg

    def assert_field_has_max_length(self, field_name, max_length):
        field = self._get_field(field_name)
        validator = self._get_validator(field, Length)
        if validator:
            msg = (
                "Field '%s' has a max length of %s, but expected the max "
                "length to be %s."
            ) % (field_name, validator.max, max_length)
            assert validator.max == max_length, msg
        else:
            raise AssertionError(
                "Field '%s' does not have a max length, but expected the max "
                "length to be %s." % (field_name, max_length)
            )
