from tests import ModelFormTestCase
from wtforms_alchemy import ModelForm


class TestFieldParameters(ModelFormTestCase):
    def test_assigns_description_from_column_info(self):
        self.init(info={'description': 'Description'})
        self.assert_description('test_column', 'Description')

    def test_assigns_descriptions_from_form_configuration(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

                field_args = {
                    'test_column': {'description': 'TESTING'}
                }

        self.form_class = ModelTestForm
        self.assert_description('test_column', 'TESTING')
