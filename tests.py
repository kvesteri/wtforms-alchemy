from datetime import datetime
import sqlalchemy as sa

from wtforms import (
    BooleanField,
    DateTimeField,
    FormField,
    SelectField,
    TextAreaField,
    TextField,
    Form,
)
from wtforms.validators import NumberRange, Length, Required, Email
from wtforms_alchemy import (
    Unique,
    ModelCreateForm,
    ModelUpdateForm,
    model_form_factory,
)
from wtforms_test import FormTestCase
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
    email = sa.Column(
        sa.Unicode(255),
        unique=True,
        nullable=False,
        info={'validators': Email()}
    )
    status = sa.Column(sa.Enum(*STATUSES))
    status2 = sa.Column(
        sa.Enum(*STATUSES),
        info={
            'choices': {
                'status1': 'some status',
                'status2': 'another status'
            }
        }
    )
    overridable_field = sa.Column(sa.Integer)
    excluded_field = sa.Column(sa.Integer)
    is_active = sa.Column(sa.Boolean)
    age = sa.Column(sa.Integer)
    level = sa.Column(sa.Integer, info={'min': 1, 'max': 100})
    description = sa.Column(sa.Unicode(255))


class Location(Base):
    __tablename__ = 'location'
    id = sa.Column(BigInteger, autoincrement=True, primary_key=True)
    name = sa.Column(
        sa.Unicode(255),
        nullable=False,
        info={
            'label': 'Name',
            'description': 'This is name of the location.'
        }
    )
    longitude = sa.Column(sa.Integer)
    latitude = sa.Column(sa.Integer)


class Event(Entity):
    __tablename__ = 'event'
    id = sa.Column(sa.BigInteger, sa.ForeignKey(Entity.id), primary_key=True)
    name = sa.Column(
        sa.Unicode(255), index=True, nullable=False, default=u'',
        info={'label': 'Name', 'description': 'The name of the event.'}
    )
    start_time = sa.Column(sa.DateTime)
    is_private = sa.Column(sa.Boolean, nullable=False)
    description = sa.Column(sa.UnicodeText, default=lambda: '')
    location_id = sa.Column(sa.BigInteger, sa.ForeignKey(Location.id))
    location = orm.relationship(Location)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


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


class UserOnlyNameForm(ModelCreateForm):
    class Meta:
        model = User
        only = ['name']


class AddressForm(Form):
    name = TextField(validators=[Required()])


class LocationForm(ModelCreateForm):
    class Meta:
        model = Location

    address = FormField(AddressForm)


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

    def test_model_form_factory_with_custom_base_class(self):
        class SomeForm(Form):
            pass

        class TestCustomBase(model_form_factory(SomeForm)):
            class Meta:
                model = Location

        assert isinstance(TestCustomBase(), SomeForm)


class TestLocationForm(FormTestCase):
    form_class = LocationForm

    def test_assigns_description_from_column_info(self):
        self.assert_description('name', 'This is name of the location.')


class TestCreateUserForm(FormTestCase):
    form_class = CreateUserForm

    def test_converts_unicode_columns_to_text_fields(self):
        self.assert_type('name', TextField)

    def test_users_may_manually_override_generated_fields(self):
        self.assert_type('overridable_field', BooleanField)

    def test_auto_assigns_length_validators(self):
        self.assert_max_length('name', 255)

    def test_assigns_validators_from_info_field(self):
        self.assert_has_validator('email', Email)

    def test_boolean_column_converts_to_boolean_field(self):
        self.assert_type('is_active', BooleanField)

    def test_supports_custom_choices_for_enum_fields(self):
        self.assert_choices(
            'status2', {
                'status1': 'some status',
                'status2': 'another status'
            }
        )

    def test_does_not_contain_surrogate_primary_keys_by_default(self):
        assert not self.has_field('id')

    def test_basic_fields_do_not_have_validators(self):
        form = CreateUserForm()
        assert form.is_active.validators == []

    def test_assigns_non_nullable_fields_as_required(self):
        self.assert_required('email')

    def test_assigns_unique_validator_for_unique_fields(self):
        self.assert_has_validator('email', Unique)

    def test_age_has_additional_validator(self):
        assert self.get_validator('age', NumberRange)

    def test_enum_field_converts_to_select_field(self):
        self.assert_type('status', SelectField)
        form = CreateUserForm()
        assert form.status.choices == [(s, s) for s in User.STATUSES]

    def test_assigns_default_values(self):
        self.assert_default('name', '')

    def test_fields_can_be_excluded(self):
        form = CreateUserForm()
        assert not hasattr(form, 'excluded_field')

    def test_adding_custom_length_validators(self):
        self.assert_min_length('description', 2)
        self.assert_max_length('description', 55)

    def test_non_nullable_fields_with_defaults_are_not_required(self):
        self.assert_not_required('name')

    def test_min_and_max_info_attributes_generate_number_range_validator(self):
        validator = self.get_validator('level', NumberRange)
        assert validator.min == 1
        assert validator.max == 100


class TestUpdateUserForm(FormTestCase):
    form_class = UpdateUserForm

    def test_does_not_assign_non_nullable_fields_as_required(self):
        self.assert_not_required('name')

    def test_all_fields_optional_by_default(self):
        self.assert_optional('name')


class TestEventForm(FormTestCase):
    form_class = EventForm

    def test_unicode_text_columns_convert_to_textarea_fields(self):
        self.assert_type('description', TextAreaField)

    def test_date_column_converts_to_date_field(self):
        self.assert_type('start_time', DateTimeField)

    def test_supports_labels(self):
        self.assert_label('name', 'Name')

    def test_supports_descriptions(self):
        self.assert_description('name', 'The name of the event.')

    def test_does_not_add_required_validators_to_non_nullable_booleans(self):
        self.assert_required('is_private')

    def test_supports_custom_datetime_format(self):
        form = self.form_class()
        assert form.start_time.format == '%Y-%m-%dT%H:%M:%S'

    def test_does_not_add_default_value_if_default_is_callable(self):
        self.assert_default('description', None)

    def test_does_not_include_datetime_columns_with_default(self):
        assert not self.has_field('created_at')


class TestUserOnlyNameForm(FormTestCase):
    form_class = UserOnlyNameForm

    def test_meta_options_support_only(self):
        form = self.form_class()
        assert len(form._fields) == 1
