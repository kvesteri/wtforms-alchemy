import sqlalchemy as sa
from pytest import raises
from sqlalchemy.ext.hybrid import hybrid_property

from tests import ModelFormTestCase
from wtforms_alchemy import ModelForm
from wtforms_alchemy.exc import AttributeTypeException


class TestHybridProperties(ModelFormTestCase):
    def test_hybrid_property_returning_column_property(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            id = sa.Column(sa.Integer, primary_key=True)
            _test_column = sa.Column('test_column', sa.Boolean, nullable=False)

            @hybrid_property
            def test_column_hybrid(self):
                return self._test_column

            @test_column_hybrid.setter
            def test_column_hybrid(self, value):
                self._test_column = value

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_str_validator = None
                not_null_validator = None
                include = ('test_column_hybrid', )
                exclude = ('_test_column', )

        form = ModelTestForm()
        assert form.test_column_hybrid

    def test_hybrid_property_returning_expression(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            id = sa.Column(sa.Integer, primary_key=True)
            _test_column = sa.Column('test_column', sa.Boolean, nullable=False)

            @hybrid_property
            def test_column_hybrid(self):
                return self._test_column + self._test_column

            @test_column_hybrid.setter
            def test_column_hybrid(self, value):
                self._test_column = value

        with raises(AttributeTypeException):
            class ModelTestForm(ModelForm):
                class Meta:
                    model = ModelTest
                    not_null_str_validator = None
                    not_null_validator = None
                    include = ('test_column_hybrid', )
                    exclude = ('_test_column', )
