import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions
from sqlalchemy_utils import force_auto_coercion
from wtforms_test import FormTestCase

from wtforms_alchemy import ModelForm

force_auto_coercion()


class MultiDict(dict):
    def getlist(self, key):
        return [self[key]]


class ModelFormTestCase(FormTestCase):
    dns = 'sqlite:///:memory:'

    def setup_method(self, method):
        self.engine = create_engine(self.dns)
        self.base = declarative_base()

    def teardown_method(self, method):
        self.engine.dispose()
        self.ModelTest = None
        self.form_class = None

    def init_model(self, type_=sa.Unicode(255), **kwargs):
        kwargs.setdefault('nullable', False)

        class ModelTest(self.base):
            __tablename__ = 'model_test'
            query = None
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(type_, **kwargs)
            some_property = 'something'

        self.ModelTest = ModelTest

    def init(self, type_=sa.Unicode(255), **kwargs):
        self.init_model(type_=type_, **kwargs)
        self.init_form()

    def init_form(self):
        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

        self.form_class = ModelTestForm


class FormRelationsTestCase(object):
    dns = 'sqlite:///:memory:'

    def setup_method(self, method):
        self.engine = create_engine(self.dns)

        self.base = declarative_base()
        self.create_models()
        self.create_forms()

        self.base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        close_all_sessions()
        self.base.metadata.drop_all(self.engine)
        self.engine.dispose()
