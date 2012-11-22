from wtforms_alchemy import Chain
from wtforms_test import FormTestCase
from wtforms import Form
from wtforms.fields import TextField
from wtforms.validators import DataRequired, Email
from tests import MultiDict


class TestChainValidator(FormTestCase):
    def test_validates_whole_chain(self):
        class MyForm(Form):
            email = TextField(validators=[Chain([DataRequired(), Email()])])

        form = MyForm(MultiDict({'name': ''}))
        form.validate()
        assert 'email' in form.errors
