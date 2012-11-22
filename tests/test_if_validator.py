from wtforms_alchemy import If
from wtforms_test import FormTestCase
from wtforms import Form
from wtforms.fields import TextField
from wtforms.validators import DataRequired
from tests import MultiDict


class TestIfValidator(FormTestCase):
    def test_only_validates_if_condition_returns_true(self):
        class MyForm(Form):
            name = TextField(validators=[
                If(
                    lambda form, field: False,
                    DataRequired(),
                )
            ])

        form = MyForm(MultiDict({'name': ''}))
        form.validate()
        assert not form.errors

    def test_encapsulates_given_validator(self):
        class MyForm(Form):
            name = TextField(validators=[
                If(
                    lambda form, field: True,
                    DataRequired(),
                )
            ])

        form = MyForm(MultiDict({'name': ''}))
        form.validate()
        assert 'name' in form.errors

    def test_supports_custom_error_messages(self):
        class MyForm(Form):
            name = TextField(validators=[
                If(
                    lambda form, field: True,
                    DataRequired(),
                    message='Validation failed.'
                )
            ])

        form = MyForm(MultiDict({'name': ''}))
        form.validate()
        assert form.errors['name'] == ['Validation failed.']
