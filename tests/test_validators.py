from pytest import raises
from unittest import TestCase
import sqlalchemy as sa
from wtforms.validators import (
    Email, StopValidation
)
from wtforms_alchemy import Unique, ModelForm
from wtforms_alchemy.generator import NotNone
from tests import ModelFormTestCase


class NotNoneValidatorTest(TestCase):
    class DummyField(object):
        def __init__(self, raw_data=None, default=None):
            self.raw_data = raw_data
            self.default = default
            self.errors = []

        def gettext(self, message):
            return message

    def test_raw_data_is_none_and_no_default(self):
        field = self.DummyField()
        validator = NotNone()

        self.assertRaises(
            StopValidation,
            validator,
            None, field
        )

        self.assertEqual(validator.message, 'This field is required.')

    def test_raw_data_is_none_with_default(self):
        field = self.DummyField(default='foo')
        NotNone()(None, field)

    def test_raw_data_is_empty_string_with_no_default(self):
        field = self.DummyField('')
        NotNone()(None, field)

    def test_raw_data_is_non_trivial_string_with_no_default(self):
        field = self.DummyField('foo')
        NotNone()(None, field)


class TestAutoAssignedValidators(ModelFormTestCase):
    def assert_required(self, field_name):
        validator = self.get_validator(field_name, NotNone)
        if validator is None:
            self.fail("Field '%s' is not required." % field_name)

    def test_auto_assigns_length_validators(self):
        self.init()
        self.assert_max_length('test_column', 255)

    def test_assigns_validators_from_info_field(self):
        self.init(info={'validators': Email()})
        self.assert_has_validator('test_column', Email)

    def test_assigns_unique_validator_for_unique_fields(self):
        self.init(unique=True)
        self.assert_has_validator('test_column', Unique)

    def test_raises_exception_if_no_session_set_for_unique_validators(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Unicode(255), unique=True)

        with raises(Exception):
            class ModelTestForm(ModelForm):
                class Meta:
                    model = ModelTest

    def test_assigns_non_nullable_fields_as_required(self):
        self.init(nullable=False)
        self.assert_required('test_column')

    def test_not_nullable_booleans_are_required(self):
        self.init(sa.Boolean, nullable=False)
        self.assert_required('test_column')

    def test_not_nullable_fields_with_defaults_are_not_required(self):
        self.init(nullable=False, default=u'default')
        self.assert_not_required('test_column')

    def test_assigns_not_nullable_integers_as_optional(self):
        self.init(sa.Integer, nullable=True)
        self.assert_optional('test_column')
