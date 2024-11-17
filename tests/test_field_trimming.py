from tests import ModelFormTestCase, MultiDict
from wtforms_alchemy import ModelForm


class TestStringFieldTrimming(ModelFormTestCase):
    def test_strip_string_fields_set_for_string_field(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                strip_string_fields = True

        f = ModelTestForm(MultiDict([("test_column", "strip this   ")]))
        assert f.test_column.data == "strip this"

    def test_does_not_trim_fields_when_trim_param_is_false(self):
        self.init(info={"trim": False})

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                strip_string_fields = True

        f = ModelTestForm(MultiDict([("test_column", "strip this   ")]))
        assert f.test_column.data == "strip this   "
