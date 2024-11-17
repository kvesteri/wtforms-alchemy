import sqlalchemy as sa
from wtforms.validators import NumberRange

from tests import ModelFormTestCase
from wtforms_alchemy import ModelForm


class TestColumnAliases(ModelFormTestCase):
    def test_supports_column_aliases(self):
        class TestModel(self.base):
            __tablename__ = "TestTable"
            id = sa.Column(sa.Integer, primary_key=True)
            some_alias = sa.Column("some_name", sa.Integer)

        class TestForm(ModelForm):
            class Meta:
                model = TestModel

        form = TestForm()
        assert hasattr(form, "some_alias")
        assert not hasattr(form, "some_name")

    def test_labels(self):
        class TestModel(self.base):
            __tablename__ = "TestTable"
            id = sa.Column(sa.Integer, primary_key=True)
            some_alias = sa.Column(
                "some_name",
                sa.Integer,
            )

        class TestForm(ModelForm):
            class Meta:
                model = TestModel

        form = TestForm()
        assert form.some_alias.label.text == "some_alias"

    def test_unique_indexes(self):
        class TestModel(self.base):
            __tablename__ = "TestTable"
            id = sa.Column(sa.Integer, primary_key=True)
            some_alias = sa.Column("some_name", sa.Integer, unique=True)

        class TestForm(ModelForm):
            class Meta:
                model = TestModel

            @staticmethod
            def get_session():
                return None

        form = TestForm()
        assert hasattr(form, "some_alias")
        assert not hasattr(form, "some_name")

    def test_meta_field_args(self):
        class TestModel(self.base):
            __tablename__ = "TestTable"
            id = sa.Column(sa.Integer, primary_key=True)
            some_alias = sa.Column("some_name", sa.Integer)

        validators = [NumberRange(max=4)]

        class TestForm(ModelForm):
            class Meta:
                model = TestModel
                field_args = {"some_alias": {"validators": validators}}

        form = TestForm()
        assert hasattr(form, "some_alias")
        assert not hasattr(form, "some_name")
        assert form.some_alias.validators == validators

    def test_additional_validators(self):
        class TestModel(self.base):
            __tablename__ = "TestTable"
            id = sa.Column(sa.Integer, primary_key=True)
            some_alias = sa.Column("some_name", sa.Integer)

        number_range = NumberRange(max=4)
        validator_list = [number_range]

        class TestForm(ModelForm):
            class Meta:
                model = TestModel
                validators = {"some_alias": validator_list}

        form = TestForm()
        assert number_range in form.some_alias.validators
