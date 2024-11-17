import sqlalchemy as sa

from tests import ModelFormTestCase


class TestFieldOrder(ModelFormTestCase):
    def setup_method(self, method):
        ModelFormTestCase.setup_method(self, method)

        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=True)
            full_description = sa.Column(sa.UnicodeText)
            description = sa.Column(sa.UnicodeText)
            start_time = sa.Column(sa.DateTime)
            end_time = sa.Column(sa.DateTime)
            category = sa.Column(sa.Unicode(255))
            entry_fee = sa.Column(sa.Numeric)
            type = sa.Column(sa.Unicode(255))

        self.ModelTest = ModelTest
        self.init_form()

    def test_field_definition_order(self):
        field_names = [field.name for field in self.form_class()]
        assert field_names == sa.inspect(self.ModelTest).attrs.keys()[1:]
