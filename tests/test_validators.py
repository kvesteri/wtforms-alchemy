from datetime import datetime, time

import sqlalchemy as sa
from sqlalchemy_utils import EmailType
from wtforms.validators import (
    DataRequired,
    Email,
    InputRequired,
    Length,
    NumberRange,
    Optional,
)
from wtforms_components import DateRange, TimeRange

from tests import ModelFormTestCase
from wtforms_alchemy import ClassMap, ModelForm, Unique


class TestAutoAssignedValidators(ModelFormTestCase):
    def test_auto_assigns_length_validators(self):
        self.init()
        self.assert_max_length("test_column", 255)

    def test_assigns_validators_from_info_field(self):
        self.init(info={"validators": Email()})
        self.assert_has_validator("test_column", Email)

    def test_assigns_unique_validator_for_unique_fields(self):
        self.init(unique=True)
        self.assert_has_validator("test_column", Unique)

    def test_assigns_non_nullable_fields_as_required(self):
        self.init(nullable=False)
        self.assert_has_validator("test_column", DataRequired)
        self.assert_has_validator("test_column", InputRequired)

    def test_type_level_not_nullable_validators(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Unicode(255), nullable=False)

        validator = DataRequired()

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_validator_type_map = ClassMap()
                not_null_validator = validator

        form = ModelTestForm()
        assert validator in form.test_column.validators

    def test_not_nullable_validator_with_type_decorator(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(EmailType, nullable=False)

        validator = DataRequired()

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_validator_type_map = ClassMap([(sa.String, validator)])
                not_null_validator = []

        form = ModelTestForm()
        assert validator in form.test_column.validators

    def test_not_null_validator_as_empty_list(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Boolean, nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_validator_type_map = ClassMap()
                not_null_validator = []

        form = ModelTestForm()
        assert list(form.test_column.validators) == []

    def test_not_null_validator_as_none(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Boolean, nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_validator_type_map = ClassMap()
                not_null_validator = None

        form = ModelTestForm()
        assert len(form.test_column.validators) == 1
        assert isinstance(form.test_column.validators[0], Optional)

    def test_not_nullable_booleans_are_required(self):
        self.init(sa.Boolean, nullable=False)
        self.assert_has_validator("test_column", InputRequired)

    def test_not_nullable_fields_with_defaults_are_not_required(self):
        self.init(nullable=False, default="default")
        self.assert_not_required("test_column")

    def test_assigns_nullable_integers_as_optional(self):
        self.init(sa.Integer, nullable=True)
        self.assert_optional("test_column")

    def test_override_email_validator(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(EmailType, nullable=True)

        def validator():
            return Email("Wrong email")

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                email_validator = validator

        form = ModelTestForm()
        assert form.test_column.validators[1].message == "Wrong email"

    def test_override_optional_validator(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(EmailType, nullable=True)

        class MyOptionalValidator:
            def __init__(self, *args, **kwargs):
                pass

            def __call__(self, form, field):
                pass

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                optional_validator = MyOptionalValidator

        form = ModelTestForm()
        assert isinstance(form.test_column.validators[0], MyOptionalValidator)

    def test_override_number_range_validator(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Integer, info={"min": 3}, nullable=True)

        def number_range(min=-1, max=-1):
            return NumberRange(min=min, max=max, message="Wrong number range")

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                number_range_validator = number_range

        form = ModelTestForm()
        assert form.test_column.validators[1].message == "Wrong number range"

    def test_override_date_range_validator(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(
                sa.DateTime, info={"min": datetime(2000, 1, 1)}, nullable=True
            )

        def date_range(min=None, max=None):
            return DateRange(min=min, max=max, message="Wrong date range")

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                date_range_validator = date_range

        form = ModelTestForm()
        assert form.test_column.validators[1].message == "Wrong date range"

    def test_override_time_range_validator(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Time, info={"min": time(14, 30)}, nullable=True)

        def time_range(min=None, max=None):
            return TimeRange(min=min, max=max, message="Wrong time")

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                time_range_validator = time_range

        form = ModelTestForm()
        assert form.test_column.validators[1].message == "Wrong time"

    def test_override_length_validator(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Unicode(255), nullable=True)

        def length(min=-1, max=-1):
            return Length(min=min, max=max, message="Wrong length")

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                length_validator = length

        form = ModelTestForm()
        assert form.test_column.validators[1].message == "Wrong length"

    def test_override_optional_validator_as_none(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Boolean, nullable=True)

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                optional_validator = None

        form = ModelTestForm()
        assert list(form.test_column.validators) == []

    def test_override_unique_validator(self):
        class ModelTest(self.base):
            __tablename__ = "model_test"
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Unicode(255), unique=True, nullable=True)

        def unique(column, get_session):
            return Unique(column, get_session=get_session, message="Not unique")

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                unique_validator = unique

            @staticmethod
            def get_session():
                return None

        form = ModelTestForm()
        assert form.test_column.validators[2].message == "Not unique"
