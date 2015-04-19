from decimal import Decimal

import sqlalchemy as sa

from tests import ModelFormTestCase


class TestNumericFieldWidgets(ModelFormTestCase):
    def test_converts_numeric_scale_to_steps(self):
        self.init(
            type_=sa.Numeric(scale=2),
        )
        form = self.form_class()
        assert 'step="0.01"' in str(form.test_column)

    def test_supports_numeric_column_without_scale(self):
        self.init(
            type_=sa.Numeric(),
        )
        form = self.form_class()
        assert 'step="any"' in str(form.test_column)

    def test_supports_step_as_info_arg(self):
        self.init(
            type_=sa.Numeric(), info={'step': '0.1'},
        )
        form = self.form_class()
        assert 'step="0.1"' in str(form.test_column)

    def test_numeric_field_with_scale_and_choices(self):
        self.init(
            type_=sa.Numeric(scale=2),
            info={'choices': [
                (Decimal('1.1'), 'choice1'),
                (Decimal('1.2'), 'choice2')
            ]},
        )
        form = self.form_class()
        assert 'step="0.1"' not in str(form.test_column)


class TestIntegerFieldWidgets(ModelFormTestCase):
    def test_supports_step_as_info_arg(self):
        self.init(
            type_=sa.Integer, info={'step': '3'},
        )
        form = self.form_class()
        assert 'step="3"' in str(form.test_column)


class TestFloatFieldWidgets(ModelFormTestCase):
    def test_supports_step_as_info_arg(self):
        self.init(
            type_=sa.Float, info={'step': '0.2'},
        )
        form = self.form_class()
        assert 'step="0.2"' in str(form.test_column)
