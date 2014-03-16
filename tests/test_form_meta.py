import sqlalchemy as sa
import pytest
from tests import ModelFormTestCase


class TestModelFormMetaWithInheritance(ModelFormTestCase):

    def test_skip_unknown_types(self, ModelForm_all):
        self.init(type_=sa.Integer)

        class ModelTestForm(ModelForm_all):
            class Meta:
                skip_unknown_types = True

        class ModelTestForm2(ModelTestForm):
            class Meta:
                model = self.ModelTest

        self.form_class = ModelTestForm2
        assert self.form_class.Meta.skip_unknown_types == True

    def test_inheritance_attributes(self, ModelForm_custom):
        self.init(type_=sa.Integer)

        class ModelTestForm(ModelForm_custom):
            class Meta:
                model = self.ModelTest

        assert ModelTestForm.test_attr == 'SomeVal'



class TestUnboundFieldsInitialization(ModelFormTestCase):
    def test_skip_unknown_types(self, ModelForm_all):
        self.init(type_=sa.Integer)

        class ModelTestForm(ModelForm_all):
            class Meta:
                model = self.ModelTest
                skip_unknown_types = True

        assert ModelTestForm.test_column
