from wtforms_alchemy import SelectMultipleField
from wtforms_test import FormTestCase
from wtforms import Form
from werkzeug.datastructures import MultiDict


class TestSelectMultipleField(FormTestCase):
    choices = (
        ('Fruits', (
            ('apple', 'Apple'),
            ('peach', 'Peach'),
            ('pear', 'Pear')
        )),
        ('Vegetables', (
            ('cucumber', 'Cucumber'),
            ('potato', 'Potato'),
            ('tomato', 'Tomato'),
        ))
    )

    def init_form(self, **kwargs):
        class TestForm(Form):
            fruits = SelectMultipleField(**kwargs)

        self.form_class = TestForm
        return self.form_class

    def test_understands_nested_choices(self):
        form_class = self.init_form(choices=self.choices)
        form = form_class(
            MultiDict([
                ('fruits', 'apple'),
                ('fruits', 'invalid')
            ])
        )
        form.validate()

        assert form.errors == {
            'fruits': [u"'invalid' is not a valid choice for this field"]
        }
