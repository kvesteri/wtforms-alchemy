import sqlalchemy as sa

from wtforms import (
    BooleanField,
    DateField,
    DateTimeField,
    FormField,
    SelectField,
    TextAreaField,
    TextField,
)
from wtforms.validators import NumberRange, Length
from wtforms_alchemy import ModelCreateForm, ModelUpdateForm
from wtforms_alchemy.test import FormTestCase
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
    age = sa.Column(sa.Integer)
    description = sa.Column(sa.Unicode(255))


class Location(Base):
    __tablename__ = 'location'
    id = sa.Column(BigInteger, autoincrement=True, primary_key=True)
    name = sa.Column(sa.Unicode(255))


class Event(Entity):
    __tablename__ = 'event'

    id = sa.Column(sa.BigInteger, sa.ForeignKey(Entity.id), primary_key=True)
    name = sa.Column(sa.Unicode(255), index=True, nullable=False, default=u'')
    start_time = sa.Column(sa.DateTime)
    is_private = sa.Column(sa.Boolean, nullable=False)
    description = sa.Column(sa.UnicodeText)
    location_id = sa.Column(sa.BigInteger, sa.ForeignKey(Location.id))
    location = orm.relationship(Location)


class CreateUserForm(ModelCreateForm):
    class Meta:
        model = User
        exclude = ['excluded_field']
        validators = {
            'age': NumberRange(15, 99),
            'description': Length(min=2, max=55),
        }

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
        datetime_format = '%Y-%m-%dT%H:%M:%S'

    location = FormField(LocationForm)


class TestModelFormConfiguration(object):
    def test_inherits_config_params_from_parent_meta(self):
        assert CreateUserForm.Meta.include == []

    def test_child_classes_override_parents_config_params(self):
        assert CreateUserForm.Meta.model == User


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
        assert not self.has_field('id')

    def test_basic_fields_do_not_have_validators(self):
        form = CreateUserForm()
        assert form.is_active.validators == []

    def test_assigns_non_nullable_fields_as_required(self):
        self.assert_field_is_required('email')

    def test_assigns_unique_validator_for_unique_fields(self):
        self.assert_field_is_unique('email')

    def test_age_has_additional_validator(self):
        assert self.get_validator('age', NumberRange)

    def test_enum_field_converts_to_select_field(self):
        self.assert_field_type('status', SelectField)
        form = CreateUserForm()
        assert form.status.choices == [(s, s) for s in User.STATUSES]

    def test_assigns_default_values(self):
        self.assert_field_default('name', '')

    def test_fields_can_be_excluded(self):
        form = CreateUserForm()
        assert not hasattr(form, 'excluded_field')

    def test_adding_custom_length_validators(self):
        self.assert_field_min_length('description', 2)
        self.assert_field_max_length('description', 55)

    def test_non_nullable_fields_with_defaults_are_not_required(self):
        self.assert_field_is_not_required('name')

    # def test_patch_data_with_validation(self):
    #     form = self.form_class(name='some name')
    #     form.validate()
    #     print form.errors
    #     print form.patch_data


class TestUpdateUserForm(FormTestCase):
    form_class = UpdateUserForm

    def test_does_not_assign_non_nullable_fields_as_required(self):
        self.assert_field_is_not_required('name')

    def test_all_fields_optional_by_default(self):
        self.assert_field_is_optional('name')

    def test_patch_data(self):
        form = self.form_class(name='some patched name')
        assert form.patch_data == {'name': 'some patched name'}


class TestEventForm(FormTestCase):
    form_class = EventForm

    def test_unicode_text_columns_convert_to_textarea_fields(self):
        self.assert_field_type('description', TextAreaField)

    def test_date_column_converts_to_date_field(self):
        self.assert_field_type('start_time', DateTimeField)

    def test_patch_data_with_form_fields(self):
        form = self.form_class(name='some patched name')
        assert form.patch_data == {'name': 'some patched name'}

    def test_does_not_add_required_validators_to_non_nullable_booleans(self):
        self.assert_field_is_required('is_private')

    def test_supports_custom_datetime_format(self):
        class MultiDict(dict):
            def getlist(self, key):
                return [self[key]]

        form = self.form_class()
        assert form.start_time.format == '%Y-%m-%dT%H:%M:%S'
