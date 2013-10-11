from pytest import raises
import sqlalchemy as sa
from wtforms.fields import IntegerField
from wtforms.validators import Email
from wtforms_alchemy import (
    InvalidAttributeException, ModelForm
)
from tests import ModelFormTestCase, MultiDict


class UnknownType(sa.types.UserDefinedType):
    def get_col_spec(self):
        return "UNKNOWN()"


class TestModelFormConfiguration(ModelFormTestCase):
    def test_skip_unknown_types(self):
        self.init(type_=UnknownType)

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                skip_unknown_types = True

        self.form_class = ModelTestForm
        assert not self.has_field('test_column')

    def test_supports_field_exclusion(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                exclude = ['test_column']

        self.form_class = ModelTestForm
        assert not self.has_field('test_column')

    def test_throws_exception_for_unknown_excluded_column(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                include = ['some_unknown_column']

        with raises(InvalidAttributeException):
            self.form_class = ModelTestForm()

    def test_throws_exception_for_non_column_fields(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                include = ['some_property']

        with raises(InvalidAttributeException):
            self.form_class = ModelTestForm()

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

    def test_inherits_config_params_from_parent_meta(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                only = ['test_column']

        class AnotherModelTestForm(ModelTestForm):
            class Meta:
                pass

        assert AnotherModelTestForm.Meta.only == ['test_column']

    def test_child_classes_override_parents_config_params(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                only = ['test_column']

        class AnotherModelTestForm(ModelTestForm):
            class Meta:
                only = []

        assert AnotherModelTestForm.Meta.only == []

    def test_strip_strings_fields(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                only = ['test_column']
                strip_string_fields = True

        form = ModelTestForm(MultiDict(test_column=u' something '))
        assert form.test_column.data == u'something'

    def test_strip_strings_fields_with_empty_values(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                only = ['test_column']
                strip_string_fields = True

        form = ModelTestForm()


