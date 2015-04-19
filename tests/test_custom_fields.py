from wtforms import Form

from tests import MultiDict
from wtforms_alchemy import null_or_unicode, SelectField


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
