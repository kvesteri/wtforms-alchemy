import sqlalchemy as sa

from wtforms import (
    BooleanField,
    DateField,
    DateTimeField,
    Field,
    SelectField,
    TextAreaField,
    TextField,
    Form,
    FormField,
)
from wtforms.validators import Required, Length, Email, Optional
from wtforms_alchemy import ModelCreateForm, ModelUpdateForm, Unique
from sqlalchemy import orm
from sqlalchemy.types import BigInteger
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Entity(Base):
    __tablename__ = 'entity'
    id = sa.Column(BigInteger, autoincrement=True, primary_key=True)


class User(Entity):
    __tablename__ = 'user'
    STATUSES = ('status1', 'status2')
    query = None

    id = sa.Column(sa.BigInteger, sa.ForeignKey(Entity.id), primary_key=True)
    name = sa.Column(sa.Unicode(255), index=True, nullable=False, default=u'')
    email = sa.Column(sa.Unicode(255), unique=True, nullable=False)
    status = sa.Column(sa.Enum(*STATUSES))
    overridable_field = sa.Column(sa.Integer)
    excluded_field = sa.Column(sa.Integer)
    is_active = sa.Column(sa.Boolean)


class Location(Base):
    __tablename__ = 'location'
    id = sa.Column(BigInteger, autoincrement=True, primary_key=True)
    name = sa.Column(sa.Unicode(255))


class Event(Entity):
    __tablename__ = 'event'

    id = sa.Column(sa.BigInteger, sa.ForeignKey(Entity.id), primary_key=True)
    name = sa.Column(sa.Unicode(255), index=True, nullable=False, default=u'')
    start_time = sa.Column(sa.Date)
    description = sa.Column(sa.UnicodeText)
    location_id = sa.Column(sa.BigInteger, sa.ForeignKey(Location.id))
    location = orm.relationship(Location)


class CreateUserForm(ModelCreateForm):
    class Meta:
        model = User
        exclude = ['excluded_field']

    deleted_at = DateTimeField()
    overridable_field = BooleanField()


class UpdateUserForm(ModelUpdateForm):
    class Meta:
        model = User


class LocationForm(ModelCreateForm):
    class Meta:
        model = Location


class EventForm(ModelCreateForm):
    class Meta:
        model = Event

    location = LocationForm()


class TestModelFormConfiguration(object):
    def test_inherits_config_params_from_parent_meta(self):
        assert CreateUserForm.Meta.include == []

    def test_child_classes_override_parents_config_params(self):
        assert CreateUserForm.Meta.model == User


class FormTestCase(object):
    form_class = None

    def _make_form(self, *args, **kwargs):
        return self.form_class(csrf_enabled=False, *args, **kwargs)

    def _get_field(self, field_name):
        form = self._make_form()
        return getattr(form, field_name)

    def _get_validator(self, field, validator_class):
        for validator in field.validators:
            if isinstance(validator, validator_class):
                return validator

    def assert_field_type(self, field_name, field_type):
        self.assert_has_field(field_name)
        assert self._get_field(field_name).__class__ is field_type

    def assert_has_field(self, field_name):
        try:
            field = self._get_field(field_name)
        except AttributeError:
            field = None
        msg = "Form does not have a field called '%s'." % field_name
        assert isinstance(field, Field), msg

    def assert_field_default(self, field_name, default):
        field = self._get_field(field_name)
        assert field.default == default

    def assert_field_label(self, field_name, label):
        field = self._get_field(field_name)
        assert field.label.text == label

    def assert_field_is_unique(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' not is unique." % field_name
        assert self._get_validator(field, Unique), msg

    def assert_field_is_not_optional(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is optional." % field_name
        assert not self._get_validator(field, Required), msg

    def assert_field_is_optional(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is not optional." % field_name
        assert self._get_validator(field, Optional), msg

    def assert_field_is_not_required(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is required." % field_name
        assert not self._get_validator(field, Required), msg

    def assert_field_is_required(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is not required." % field_name
        assert self._get_validator(field, Required), msg

    def assert_field_must_be_valid_email_address(self, field_name):
        field = self._get_field(field_name)
        msg = (
            "Field '%s' is not required to be a valid email address." %
            field_name
        )
        assert self._get_validator(field, Email), msg

    def assert_field_has_max_length(self, field_name, max_length):
        field = self._get_field(field_name)
        validator = self._get_validator(field, Length)
        if validator:
            msg = (
                "Field '%s' has a max length of %s, but expected the max "
                "length to be %s."
            ) % (field_name, validator.max, max_length)
            assert validator.max == max_length, msg
        else:
            raise AssertionError(
                "Field '%s' does not have a max length, but expected the max "
                "length to be %s." % (field_name, max_length)
            )


class TestCreateUserForm(FormTestCase):
    form_class = CreateUserForm

    def test_converts_unicode_columns_to_text_fields(self):
        self.assert_field_type('name', TextField)

    def test_users_may_manually_override_generated_fields(self):
        self.assert_field_type('overridable_field', BooleanField)

    def test_auto_assigns_length_validators(self):
        self.assert_field_has_max_length('name', 255)

    def test_boolean_column_converts_to_boolean_field(self):
        self.assert_field_type('is_active', BooleanField)

    def test_does_not_contain_surrogate_primary_keys_by_default(self):
        form = CreateUserForm()
        assert not hasattr(form, 'id')

    def test_basic_fields_do_not_have_validators(self):
        form = CreateUserForm()
        assert form.is_active.validators == []

    def test_assigns_non_nullable_fields_as_required(self):
        self.assert_field_is_required('name')

    def test_assigns_unique_validator_for_unique_fields(self):
        self.assert_field_is_unique('email')

    def test_enum_field_converts_to_select_field(self):
        self.assert_field_type('status', SelectField)
        form = CreateUserForm()
        assert form.status.choices == [(s, s) for s in User.STATUSES]

    def test_assigns_default_values(self):
        self.assert_field_default('name', '')

    def test_fields_can_be_excluded(self):
        form = CreateUserForm()
        assert not hasattr(form, 'excluded_field')


class TestUpdateUserForm(FormTestCase):
    form_class = UpdateUserForm

    def test_does_not_assign_non_nullable_fields_as_required(self):
        self.assert_field_is_not_required('name')

    def test_all_fields_optional_by_default(self):
        self.assert_field_is_optional('name')


class TestEventForm(FormTestCase):
    form_class = EventForm

    def test_unicode_text_columns_convert_to_textarea_fields(self):
        self.assert_field_type('description', TextAreaField)

    def test_supports_relations(self):
        form = EventForm()
        assert 'name' in form.location

    def test_date_column_converts_to_date_field(self):
        self.assert_field_type('start_time', DateField)
