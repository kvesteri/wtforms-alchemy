import enum
import sqlalchemy as sa
from tests import MultiDict, ModelFormTestCase


class TestEnumSelectField(ModelFormTestCase):
    def setup_method(self, method):
        super().setup_method(method)

        class TestEnum(enum.Enum):
            A = 'a'
            B = 'b'
    
        self.init(type_=sa.Enum(TestEnum), nullable=True)

    def test_valid_options(self):
        for option in ['a', 'b']:
            form = self.form_class(MultiDict(test_column=option))
            assert form.validate()
            assert len(form.errors) == 0

    def test_invalid_options(self):
        for option in ['c', 'unknown']:
            form = self.form_class(MultiDict(test_column=option))
            assert not form.validate()
            assert len(form.errors['test_column']) == 2
