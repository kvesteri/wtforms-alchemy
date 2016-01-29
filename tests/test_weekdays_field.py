from wtforms import Form

from tests import MultiDict
from wtforms_alchemy import WeekDaysField


class TestWeekDaysField(object):
    def init_form(self, **kwargs):
        class TestForm(Form):
            test_field = WeekDaysField(**kwargs)
        return TestForm

    def test_valid_weekdays(self):
        form_class = self.init_form()
        form = form_class(MultiDict(test_field=0))
        form.validate()
        assert len(form.errors) == 0

    def test_invalid_weekdays(self):
        form_class = self.init_form()
        form = form_class(MultiDict([
            ('test_field', '8'),
        ]))
        form.validate()
        assert len(form.errors['test_field']) == 1
