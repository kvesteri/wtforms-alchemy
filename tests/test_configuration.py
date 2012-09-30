import sqlalchemy as sa
from wtforms.fields import IntegerField
from wtforms.validators import Email
from wtforms_alchemy import ModelForm
from tests import ModelFormTestCase


class TestModelFormConfiguration(ModelFormTestCase):
    def test_supports_field_exclusion(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                exclude = ['test_column']

        self.form_class = ModelTestForm
        assert not self.has_field('test_column')

    def test_supports_field_inclusion(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                include = ['id']

        self.form_class = ModelTestForm
        assert self.has_field('id')

    def test_supports_only_attribute(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            query = None
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.UnicodeText)
            test_column2 = sa.Column(sa.UnicodeText)

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                only = ['test_column']

        form = ModelTestForm()
        assert len(form._fields) == 1

    def test_supports_field_overriding(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

            test_column = IntegerField()

        self.form_class = ModelTestForm
        self.assert_type('test_column', IntegerField)

    def test_supports_assigning_all_fields_as_optional(self):
        self.init(nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                all_fields_optional = True

        self.form_class = ModelTestForm
        self.assert_not_required('test_column')
        self.assert_optional('test_column')

    def test_supports_custom_datetime_format(self):
        self.init(sa.DateTime, nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                datetime_format = '%Y-%m-%dT%H:%M:%S'

        form = ModelTestForm()
        assert form.test_column.format == '%Y-%m-%dT%H:%M:%S'

    def test_supports_additional_validators(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                validators = {'test_column': Email()}

        self.form_class = ModelTestForm
        self.assert_has_validator('test_column', Email)
