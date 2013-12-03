import sqlalchemy as sa
from wtforms_alchemy import ModelForm
from tests import ModelFormTestCase


class TestColumnAliases(ModelFormTestCase):
    def test_supports_column_aliases(self):
        class TestModel(self.base):
            __tablename__ = 'TestTable'
            id = sa.Column(sa.Integer, primary_key=True)
            new_name = sa.Column('oldname', sa.Integer)

        class TestForm(ModelForm):
            class Meta:
                model = TestModel

        form = TestForm()
        assert hasattr(form, 'new_name')
        assert not hasattr(form, 'old_name')
