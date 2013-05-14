from pytest import raises
import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from wtforms_alchemy import ModelForm
from tests import ModelFormTestCase


class TestInternationalizationExtension(ModelFormTestCase):
    def init(self):
        class ModelTest(self.base, Translatable):
            __tablename__ = 'model_test'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.Unicode(255))
            ]
            id = sa.Column(sa.Integer, primary_key=True)
            some_property = 'something'

        self.ModelTest = ModelTest
        sa.orm.configure_mappers()
        Session = sa.orm.sessionmaker(bind=self.engine)
        self.session = Session()

        self.init_form()

    def test_supports_translated_columns(self):
        self.init()
        form = self.form_class()
        assert form.name
        assert form.content

    def test_supports_field_exclusion(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                exclude = ['name']

        with raises(AttributeError):
            ModelTestForm().name
