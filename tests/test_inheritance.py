from wtforms import Form
from wtforms_test import FormTestCase

from wtforms_alchemy import model_form_factory, ModelForm


class TestInheritance(FormTestCase):
    class Base(Form):
        @classmethod
        def get_session(self):
            return 'TestSession'

    def test_default_base(self):
        assert ModelForm.get_session is None

    def test_custom_base_without_session(self):
        cls = model_form_factory(Form)
        assert cls.get_session is None

    def test_custom_base_with_session(self):
        cls = model_form_factory(self.Base)
        assert cls.get_session() == 'TestSession'

    def test_inherit_with_new_session(self):
        cls = model_form_factory(self.Base)

        class Sub(cls):
            @classmethod
            def get_session(self):
                return 'SubTestSession'
        assert Sub.get_session() == 'SubTestSession'

    def test_inherit_without_new_session(self):
        cls = model_form_factory(self.Base)

        class Sub(cls):
            pass
        assert Sub.get_session() == 'TestSession'
