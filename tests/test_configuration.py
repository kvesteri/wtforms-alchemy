import sqlalchemy as sa
from pytest import raises
from wtforms.fields import IntegerField
from wtforms.validators import Email

from tests import ModelFormTestCase, MultiDict
from wtforms_alchemy import (
    AttributeTypeException,
    InvalidAttributeException,
    ModelForm,
)


class UnknownType(sa.types.UserDefinedType):
    def get_col_spec(self):
        return "UNKNOWN()"


class TestModelFormConfiguration(ModelFormTestCase):
    def test_skip_unknown_types(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            query = None
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(UnknownType)
            some_property = "something"

        self.ModelTest = ModelTest

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                skip_unknown_types = True

        self.form_class = ModelTestForm
        assert not self.has_field("test_column")

    def test_supports_field_exclusion(self):
        self.init_model()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                exclude = ["test_column"]

        self.form_class = ModelTestForm
        assert not self.has_field("test_column")

    def test_throws_exception_for_unknown_excluded_column(self):
        self.init_model()

        with raises(InvalidAttributeException):

            class ModelTestForm(ModelForm):
                class Meta:
                    model = self.ModelTest
                    exclude = ["some_unknown_column"]

    def test_invalid_exclude_with_attr_errors_as_false(self):
        self.init_model()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                attr_errors = False
                exclude = ["some_unknown_column"]

    def test_throws_exception_for_unknown_included_column(self):
        self.init_model()

        with raises(InvalidAttributeException):

            class ModelTestForm(ModelForm):
                class Meta:
                    model = self.ModelTest
                    include = ["some_unknown_column"]

    def test_invalid_include_with_attr_errors_as_false(self):
        self.init_model()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                attr_errors = False
                include = ["some_unknown_column"]

    def test_throws_exception_for_non_column_fields(self):
        self.init_model()

        with raises(AttributeTypeException):

            class ModelTestForm(ModelForm):
                class Meta:
                    model = self.ModelTest
                    include = ["some_property"]

    def test_supports_field_inclusion(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                include = ["id"]

        self.form_class = ModelTestForm
        assert self.has_field("id")

    def test_supports_only_attribute(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            query = None
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.UnicodeText)
            test_column2 = sa.Column(sa.UnicodeText)

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                only = ["test_column"]

        form = ModelTestForm()
        assert len(form._fields) == 1

    def test_supports_field_overriding(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

            test_column = IntegerField()

        self.form_class = ModelTestForm
        self.assert_type("test_column", IntegerField)

    def test_supports_assigning_all_fields_as_optional(self):
        self.init(nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                all_fields_optional = True

        self.form_class = ModelTestForm
        self.assert_not_required("test_column")
        self.assert_optional("test_column")

    def test_supports_custom_datetime_format(self):
        self.init(sa.DateTime, nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                datetime_format = "%Y-%m-%dT%H:%M:%S"

        form = ModelTestForm()
        assert form.test_column.format == ["%Y-%m-%dT%H:%M:%S"]

    def test_supports_additional_validators(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                validators = {"test_column": Email()}

        self.form_class = ModelTestForm
        self.assert_has_validator("test_column", Email)

    def test_inherits_config_params_from_parent_meta(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                only = ["test_column"]

        class AnotherModelTestForm(ModelTestForm):
            class Meta:
                pass

        assert AnotherModelTestForm.Meta.only == ["test_column"]

    def test_child_classes_override_parents_config_params(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                only = ["test_column"]

        class AnotherModelTestForm(ModelTestForm):
            class Meta:
                only = []

        assert AnotherModelTestForm.Meta.only == []

    def test_strip_strings_fields(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                only = ["test_column"]
                strip_string_fields = True

        form = ModelTestForm(MultiDict(test_column=" something "))
        assert form.test_column.data == "something"

    def test_strip_strings_fields_with_empty_values(self):
        self.init()

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest
                only = ["test_column"]
                strip_string_fields = True

        ModelTestForm()

    def test_class_meta_regression(self):
        self.init()

        class SomeForm(ModelForm):
            class Meta:
                model = self.ModelTest
                foo = 9

        class OtherForm(SomeForm):
            class Meta:
                pass

        assert issubclass(OtherForm.Meta, SomeForm.Meta)
        form = OtherForm()

        # Create a side effect on the base meta.
        assert form.Meta.foo == 9
        SomeForm.Meta.foo = 12
        assert form.Meta.foo == 12
