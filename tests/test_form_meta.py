import sqlalchemy as sa
from wtforms_alchemy import ModelForm
from tests import ModelFormTestCase


class TestModelFormMetaWithInheritance(ModelFormTestCase):
    def test_skip_unknown_types(self):
        self.init(type_=sa.Integer)

        class ModelTestForm(ModelForm):
            class Meta:
                skip_unknown_types = True

        class ModelTestForm2(ModelTestForm):
            class Meta:
                model = self.ModelTest

        self.form_class = ModelTestForm2
        assert self.form_class.Meta.skip_unknown_types == True


class TestUnboundFieldsInitialization(ModelFormTestCase):
    def test_skip_unknown_types(self):
        self.init(type_=sa.Integer)

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                skip_unknown_types = True

        assert ModelTestForm.test_column
