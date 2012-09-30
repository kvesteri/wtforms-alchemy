import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from wtforms_test import FormTestCase
from wtforms_alchemy import ModelForm


class MultiDict(dict):
    def getlist(self, key):
        return [self[key]]


class ModelFormTestCase(FormTestCase):
    def setup_method(self, method):
        self.engine = create_engine('sqlite:///:memory:')
        self.base = declarative_base()

    def teardown_method(self, method):
        self.engine.dispose()

    def init(self, type_=sa.Unicode(255), **kwargs):
        kwargs.setdefault('nullable', False)

        class ModelTest(self.base):
            __tablename__ = 'model_test'
            query = None
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(type_, **kwargs)

        self.ModelTest = ModelTest
        self.init_form()

    def init_form(self):
        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

        self.form_class = ModelTestForm


class FormRelationsTestCase(object):
    def setup_method(self, method):
        self.engine = create_engine('sqlite:///:memory:')

        self.base = declarative_base()
        self.create_models()
        self.create_forms()

        self.base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.base.metadata.drop_all(self.engine)
        self.engine.dispose()
