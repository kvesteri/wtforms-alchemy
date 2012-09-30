from wtforms import Form
from wtforms_alchemy import SelectField, null_or_unicode
from tests import MultiDict


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
