#import pytz
import six
from wtforms import Form
from wtforms.form import FormMeta
from wtforms_components import (
    DateRange,
    NumberRangeField,
    PhoneNumberField,
    SelectField,
    SelectMultipleField,
    Unique,
)
from .utils import (
    is_date_column,
    is_integer_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
    class_list,
    properties,
)
from .exc import InvalidAttributeException, UnknownTypeException
from .fields import ModelFieldList, ModelFormField
from .generator import FormGenerator


__all__ = (
    DateRange,
    InvalidAttributeException,
    ModelFieldList,
    ModelFormField,
    NumberRangeField,
    PhoneNumberField,
    SelectField,
    SelectMultipleField,
    Unique,
    UnknownTypeException,
    is_date_column,
    is_integer_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
)


__version__ = '0.8.6'


class ModelFormMeta(FormMeta):
    """Meta class that overrides WTForms base meta class. The primary purpose
    of this class is allowing ModelForms use special configuration params under
    the 'Meta' class namespace.

    ModelForm classes inherit parent's Meta class properties.
    """
    def __init__(cls, *args, **kwargs):
        property_dict = {}
        for class_ in reversed(class_list(cls)):
            if hasattr(class_, 'Meta'):
                property_dict.update(class_.Meta.__dict__)

        cls.Meta = type('Meta', (object, ), property_dict)

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

            skip_unknown_types = defaults.get('skip_unknown_types', False)

            #: Whether or not to assign non-nullable fields as required
            assign_required = defaults.get('assign_required', True)

            #: Whether or not to assign all fields as optional, useful when
            #: creating update forms for patch requests
            all_fields_optional = defaults.get('all_fields_optional', False)

            validators = {}

            #: A dict with keys as field names and values as field arguments.
            field_args = {}

            #: A dict with keys as field names and values as widget options.
            widget_options = {}

            #: Whether or not to include only indexed fields.
            only_indexed_fields = defaults.get('only_indexed_fields', False)

            #: Whether or not to include primary keys.
            include_primary_keys = defaults.get('include_primary_keys', False)

            #: Whether or not to include foreign keys. By default this is False
            #: indicating that foreign keys are not included in the generated
            #: form.
            include_foreign_keys = defaults.get('include_foreign_keys', False)

            #: Whether or not to strip string fields
            strip_string_fields = defaults.get('strip_string_fields', False)

            #: Whether or not to include datetime columns that have a default
            #: value. A good example is created_at column which has a default
            #: value of datetime.utcnow.
            include_datetimes_with_default = defaults.get(
                'include_datetimes_with_default', False
            )

            #: Which form generator to use. Only override this if you have a
            #: valid form generator which you want to use instead of the
            #: default one.
            form_generator = defaults.get(
                'form_generator', FormGenerator
            )

            #: Default date format
            date_format = defaults.get('date_format', '%Y-%m-%d')

            #: Default datetime format
            datetime_format = defaults.get(
                'datetime_format', '%Y-%m-%d %H:%M:%S'
            )

            #: Additional fields to include in the generated form.
            include = []

            #: List of fields to exclude from the generated form.
            exclude = []

            #: List of fields to only include in the generated form.
            only = []

        def __init__(self, *args, **kwargs):
            """Sets object as form attribute."""

            self._obj = kwargs.get('obj', None)
            super(ModelForm, self).__init__(*args, **kwargs)

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
