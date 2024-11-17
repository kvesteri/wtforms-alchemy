from tests import ModelFormTestCase
from wtforms_alchemy import ModelForm


class TestFieldLabels(ModelFormTestCase):
    def test_assigns_labels_from_column_info(self):
        self.init(info={"label": "Test Column"})
        self.assert_label("test_column", "Test Column")

    def test_assigns_labels_from_form_configuration(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

                field_args = {"test_column": {"label": "TESTING"}}

        self.form_class = ModelTestForm
        self.assert_label("test_column", "TESTING")
