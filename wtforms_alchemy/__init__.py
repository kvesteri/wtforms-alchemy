#import pytz
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


def class_list(cls):
    """Simple recursive function for listing the parent classes of given class.
    Used by the ModelFormMeta class.
    """
    list_of_parents = [cls]
    for parent in cls.__bases__:
        list_of_parents.extend(class_list(parent))
    return list_of_parents


def properties(cls):
    return dict((name, getattr(cls, name)) for name in dir(cls))


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
                property_dict.update(properties(class_.Meta))

        cls.Meta = type('Meta', (object, ), property_dict)

        return FormMeta.__init__(cls, *args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.Meta.model:
            generator = cls.Meta.form_generator(cls)
            generator.create_form(cls)

        return FormMeta.__call__(cls, *args, **kwargs)


def model_form_factory(base=Form):
    """Creates new model form, with given base class."""

    class ModelForm(base):
        __metaclass__ = ModelFormMeta

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

            #: Whether or not to assign non-nullable fields as required
            assign_required = True

            #: Whether or not to assign all fields as optional, useful when
            #: creating update forms for patch requests
            all_fields_optional = False

            validators = {}

            #: Whether or not to include only indexed fields.
            only_indexed_fields = False

            #: Whether or not to include primary keys.
            include_primary_keys = False

            #: Whether or not to include foreign keys. By default this is False
            #: indicating that foreign keys are not included in the generated
            #: form.
            include_foreign_keys = False

            #: Whether or not to include datetime columns that have a default
            #: value. A good example is created_at column which has a default
            #: value of datetime.utcnow.
            include_datetimes_with_default = False

            #: Which form generator to use. Only override this if you have a
            #: valid form generator which you want to use instead of the
            #: default one.
            form_generator = FormGenerator

            #: Default date format
            date_format = '%Y-%m-%d'

            #: Default datetime format
            datetime_format = '%Y-%m-%d %H:%M:%S'

            #: Additional fields to include in the generated form.
            include = []

            #: List of fields to exclude from the generated form.
            exclude = []

            #: List of fields to only include in the generated form.
            only = []

        def __init__(self, *args, **kwargs):
            """Sets object as form attribute."""

            if 'obj' in kwargs:
                self._obj = kwargs['obj']
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
