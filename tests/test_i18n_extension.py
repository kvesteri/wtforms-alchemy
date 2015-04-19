import sqlalchemy as sa
from pytest import raises
from sqlalchemy_i18n import make_translatable, Translatable, translation_base

from tests import ModelFormTestCase, MultiDict
from wtforms_alchemy import ModelForm

make_translatable()


class TestInternationalizationExtension(ModelFormTestCase):
    def init(self):
        class ModelTest(self.base, Translatable):
            __tablename__ = 'model_test'
            __translatable__ = {
                'locales': ['fi', 'en']
            }

            id = sa.Column(sa.Integer, primary_key=True)
            some_property = 'something'

            locale = 'en'

        class ModelTranslation(translation_base(ModelTest)):
            __tablename__ = 'model_translation'

            name = sa.Column(sa.Unicode(255))
            content = sa.Column(sa.Unicode(255))

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

    def test_model_population(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

        form = ModelTestForm(
            MultiDict([('name', u'something'), ('content', u'something')])
        )
        obj = self.ModelTest()
        form.populate_obj(obj)
        assert obj.name == u'something'
        assert obj.content == u'something'
