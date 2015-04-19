import sqlalchemy as sa

from tests import ModelFormTestCase


class TestModelFormMetaWithInheritance(ModelFormTestCase):

    def test_skip_unknown_types(self, model_form_all):
        self.init(type_=sa.Integer)

        class ModelTestForm(model_form_all):
            class Meta:
                skip_unknown_types = True

        class ModelTestForm2(ModelTestForm):
            class Meta:
                model = self.ModelTest

        self.form_class = ModelTestForm2
        assert self.form_class.Meta.skip_unknown_types is True

    def test_inheritance_attributes(self, model_form_custom):
        self.init(type_=sa.Integer)

        class ModelTestForm(model_form_custom):
            class Meta:
                model = self.ModelTest

        assert ModelTestForm.test_attr == 'SomeVal'


class TestUnboundFieldsInitialization(ModelFormTestCase):
    def test_skip_unknown_types(self, model_form_all):
        self.init(type_=sa.Integer)

        class ModelTestForm(model_form_all):
            class Meta:
                model = self.ModelTest
                skip_unknown_types = True

        assert ModelTestForm.test_column
