import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from tests import ModelFormTestCase
from wtforms_alchemy import ModelForm


class TestSynonym(ModelFormTestCase):
    def test_synonym_returning_column_property_with_include(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            id = sa.Column(sa.Integer, primary_key=True)
            _test_column = sa.Column('test_column', sa.Integer, nullable=False)

            @hybrid_property
            def test_column_hybrid(self):
                return self.test_column * 2

            @test_column_hybrid.setter
            def test_column_hybrid(self, value):
                self._test_column = value

            test_column = sa.orm.synonym(
                '_test_column', descriptor='test_column_hybrid'
            )

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_str_validator = None
                not_null_validator = None
                include = ('test_column', )
                exclude = ('_test_column', )

        form = ModelTestForm()
        assert form.test_column

    def test_synonym_returning_column_property_with_only(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            id = sa.Column(sa.Integer, primary_key=True)
            _test_column = sa.Column('test_column', sa.Integer, nullable=False)

            @hybrid_property
            def test_column_hybrid(self):
                return self.test_column * 2

            @test_column_hybrid.setter
            def test_column_hybrid(self, value):
                self._test_column = value

            test_column = sa.orm.synonym(
                '_test_column', descriptor='test_column_hybrid'
            )

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_str_validator = None
                not_null_validator = None
                only = ('test_column', )

        form = ModelTestForm()
        assert form.test_column
