from tests import ModelFormTestCase
from sqlalchemy_defaults import Column, make_lazy_configured
import sqlalchemy as sa

class TestSQLAlchemyDefaults(ModelFormTestCase):

    def init_model(self, type_=sa.Unicode(255), **kwargs):
        """ Uses sqlalchemy_defaults.Column instead of sa.Column. """
        kwargs.setdefault('nullable', False)

        class ModelTest(self.base):
            __tablename__ = 'model_test'
            __lazy_options__ = {}
            query = None
            id = Column(sa.Integer, primary_key=True)
            test_column = Column(type_, **kwargs)
            some_property = 'something'

        self.ModelTest = ModelTest

    def test_auto_now(self):
        make_lazy_configured(sa.orm.mapper)
        self.init(sa.DateTime, auto_now=True)
        print self.base.metadata.sorted_tables
        assert "Got here"
