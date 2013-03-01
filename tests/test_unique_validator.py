from pytest import raises
import sqlalchemy as sa

from wtforms_alchemy import Unique, ModelForm
from wtforms import Form
from wtforms.fields import TextField
from tests import MultiDict, FormRelationsTestCase


class TestUniqueValidator(FormRelationsTestCase):
    def create_models(self):
        class User(self.base):
            __tablename__ = 'event'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255), unique=True)

        self.User = User

    def create_forms(self):
        class UserForm(ModelForm):
            class Meta:
                model = self.User

    def test_raises_exception_if_improperly_configured(self):
        with raises(Exception):
            class MyForm(Form):
                name = TextField(
                    validators=[Unique(
                        self.User.name,
                    )]
                )

    def test_validates_model_field_unicity(self):
        class MyForm(Form):
            name = TextField(
                validators=[Unique(
                    self.User.name,
                    get_session=lambda: self.session
                )]
            )

        self.session.add(self.User(name=u'someone'))

        form = MyForm(MultiDict({'name': u'someone'}))
        form.validate()
        assert form.errors == {'name': [u'Already exists.']}

    def test_supports_model_query_parameter(self):
        self.User.query = self.session.query(self.User)

        class MyForm(Form):
            name = TextField(
                validators=[Unique(
                    self.User.name,
                )]
            )

        form = MyForm(MultiDict({'name': u'someone'}))
        form.validate()
