from wtforms import (
    BooleanField,
    DateTimeField,
    Form,
)
from wtforms.validators import NumberRange, Length
from wtforms_alchemy import (
    ModelCreateForm,
    SelectField,
    model_form_factory,
    null_or_unicode,
)
from .models import User, Location
from tests import MultiDict


class CreateUserForm(ModelCreateForm):
    class Meta:
        model = User
        exclude = ['excluded_field']
        validators = {
            'age': NumberRange(15, 99),
            'description': Length(min=2, max=55),
        }

    deleted_at = DateTimeField()
    overridable_field = BooleanField()


class TestModelFormConfiguration(object):
    def test_inherits_config_params_from_parent_meta(self):
        assert CreateUserForm.Meta.include == []

    def test_child_classes_override_parents_config_params(self):
        assert CreateUserForm.Meta.model == User

    def test_model_form_factory_with_custom_base_class(self):
        class SomeForm(Form):
            pass

        class TestCustomBase(model_form_factory(SomeForm)):
            class Meta:
                model = Location

        assert isinstance(TestCustomBase(), SomeForm)


class TestSelectField(object):
    def test_understands_none_values(self):
        class MyForm(Form):
            choice_field = SelectField(
                choices=[('', '-- Choose --'), ('choice 1', 'Something')],
                coerce=null_or_unicode
            )

        form = MyForm(MultiDict({'choice_field': u''}))
        form.validate()
        assert form.errors == {}
