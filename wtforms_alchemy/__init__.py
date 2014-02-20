#import pytz
import six
import sqlalchemy as sa
from wtforms import Form
from wtforms.validators import (
    InputRequired, DataRequired, NumberRange, Length, Optional
)
from wtforms.form import FormMeta
from wtforms_components import (
    DateRange,
    Email,
    PhoneNumberField,
    SelectField,
    SelectMultipleField,
    Unique,
    TimeRange
)
from .utils import (
    is_date_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
    ClassMap
)
from .exc import (
    AttributeTypeException,
    InvalidAttributeException,
    UnknownTypeException,
    UnknownConfigurationOption
)
from .fields import ModelFieldList, ModelFormField
from .generator import FormGenerator


__all__ = (
    AttributeTypeException,
    DateRange,
    InvalidAttributeException,
    ModelFieldList,
    ModelFormField,
    PhoneNumberField,
    SelectField,
    SelectMultipleField,
    Unique,
    UnknownTypeException,
    is_date_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
)


__version__ = '0.12.2'


class ModelFormMeta(FormMeta):
    """Meta class that overrides WTForms base meta class. The primary purpose
    of this class is allowing ModelForms use special configuration params under
    the 'Meta' class namespace.

    ModelForm classes inherit parent's Meta class properties.
    """
    def __init__(cls, *args, **kwargs):
        bases = []
        for class_ in cls.__mro__:
            if 'Meta' in class_.__dict__:
                bases.append(getattr(class_, 'Meta'))

        cls.Meta = type('Meta', tuple(bases), {})

        FormMeta.__init__(cls, *args, **kwargs)

        if hasattr(cls.Meta, 'model') and cls.Meta.model:
            generator = cls.Meta.form_generator(cls)
            generator.create_form(cls)


def model_form_factory(base=Form, meta=ModelFormMeta, **defaults):
    """Creates new model form, with given base class."""

    class ModelForm(six.with_metaclass(meta, base)):
        """
        A function that returns SQLAlchemy session. This should be
        assigned if you wish to use Unique validator. If you are using
        Flask-SQLAlchemy along with WTForms-Alchemy you don't need to
        set this.
        """
        get_session = None

        class Meta:
            model = None

            default = None

            #: Whether or not to skip unknown types. If this is set to True,
            #: fields with types that are not present in FormGenerator type map
            #: will be silently excluded from the generated form.
            #:
            #: By default this is set to False, meaning unknown types throw
            #: exceptions when encountered.
            skip_unknown_types = defaults.pop('skip_unknown_types', False)

            #: Whether or not to assign all fields as optional, useful when
            #: creating update forms for patch requests
            all_fields_optional = defaults.pop('all_fields_optional', False)

            validators = defaults.pop('validators', {})

            #: A dict with keys as field names and values as field arguments.
            field_args = defaults.pop('field_args', {})

            #: A dict with keys as field names and values as widget options.
            widget_options = defaults.pop('widget_options', {})

            #: Whether or not to include only indexed fields.
            only_indexed_fields = defaults.pop('only_indexed_fields', False)

            #: Whether or not to include primary keys.
            include_primary_keys = defaults.pop('include_primary_keys', False)

            #: Whether or not to include foreign keys. By default this is False
            #: indicating that foreign keys are not included in the generated
            #: form.
            include_foreign_keys = defaults.pop('include_foreign_keys', False)

            #: Whether or not to strip string fields
            strip_string_fields = defaults.pop('strip_string_fields', False)

            #: Whether or not to include datetime columns that have a default
            #: value. A good example is created_at column which has a default
            #: value of datetime.utcnow.
            include_datetimes_with_default = defaults.pop(
                'include_datetimes_with_default', False
            )

            #: The default validator to be used for not nullable columns. Set
            #: this to `None` if you wish to disable it.
            not_null_validator = defaults.pop(
                'not_null_validator',
                InputRequired()
            )

            #: A dictionary that overrides not null validation on type level.
            #: Keys should be valid SQLAlchemy types and values should be valid
            #: WTForms validators.
            not_null_validator_type_map = defaults.pop(
                'not_null_validator_type_map',
                ClassMap(
                    [(sa.String, [InputRequired(), DataRequired()])]
                )
            )

            #: Default email validator
            email_validator = Email

            #: Default length validator
            length_validator = Length

            #: Default unique validator
            unique_validator = Unique

            #: Default number range validator
            number_range_validator = NumberRange

            #: Default date range validator
            date_range_validator = DateRange

            #: Default time range validator
            time_range_validator = TimeRange

            #: Default optional validator
            optional_validator = Optional

            #: Which form generator to use. Only override this if you have a
            #: valid form generator which you want to use instead of the
            #: default one.
            form_generator = defaults.pop(
                'form_generator', FormGenerator
            )

            #: Default date format
            date_format = defaults.pop('date_format', '%Y-%m-%d')

            #: Default datetime format
            datetime_format = defaults.pop(
                'datetime_format', '%Y-%m-%d %H:%M:%S'
            )

            #: Dictionary of SQLAlchemy types as keys and WTForms field classes
            #: as values. The key value pairs of this dictionary override
            #: the key value pairs of FormGenerator.TYPE_MAP.
            #:
            #: Using this configuration option one can easily configure the
            #: type conversion in class level.
            type_map = defaults.pop('type_map', ClassMap())

            #: Whether or not to raise InvalidAttributExceptions when invalid
            #: attribute names are given for include / exclude or only
            attr_errors = defaults.pop('attr_errors', True)

            #: Additional fields to include in the generated form.
            include = defaults.pop('include', [])

            #: List of fields to exclude from the generated form.
            exclude = defaults.pop('exclude', [])

            #: List of fields to only include in the generated form.
            only = defaults.pop('only', [])

        def __init__(self, *args, **kwargs):
            """Sets object as form attribute."""

            self._obj = kwargs.get('obj', None)
            super(ModelForm, self).__init__(*args, **kwargs)

    if defaults:
        raise UnknownConfigurationOption(
            list(defaults.keys())[0]
        )

    return ModelForm


ModelForm = model_form_factory(Form)


class ModelCreateForm(ModelForm):
    pass


class ModelUpdateForm(ModelForm):
    class Meta:
        all_fields_optional = True
        assign_required = False


class ModelSearchForm(ModelForm):
    class Meta:
        all_fields_optional = True
        only_indexed_fields = True
        include_primary_keys = True
