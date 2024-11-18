import sqlalchemy as sa
from wtforms import Form
from wtforms.form import FormMeta
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    URL,
)
from wtforms_components import DateRange, Email, TimeRange

from .exc import (
    AttributeTypeException,
    InvalidAttributeException,
    UnknownConfigurationOption,
    UnknownTypeException,
)
from .fields import (  # noqa
    CountryField,
    GroupedQuerySelectField,
    GroupedQuerySelectMultipleField,
    ModelFieldList,
    ModelFormField,
    PhoneNumberField,
    QuerySelectField,
    QuerySelectMultipleField,
    WeekDaysField,
)
from .generator import FormGenerator
from .utils import (
    ClassMap,
    is_date_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
)
from .validators import Unique  # noqa

__all__ = (
    AttributeTypeException,
    CountryField,
    DateRange,
    InvalidAttributeException,
    ModelFieldList,
    ModelFormField,
    PhoneNumberField,
    Unique,
    UnknownTypeException,
    is_date_column,
    is_scalar,
    null_or_int,
    null_or_unicode,
)


__version__ = "0.19.0"


def model_form_meta_factory(base=FormMeta):
    """
    Create a new class usable as a metaclass for the
    :func:`model_form_factory`. You only need to concern yourself with this if
    you desire to have a custom metclass. Otherwise, a default class is
    created and is used as a metaclass on :func:`model_form_factory`.

    :param base: The base class to use for the meta class. This is an optional
                 parameter that defaults to :class:`.FormMeta`. If you want to
                 provide your own, your class must derive from this class and
                 not directly from ``type``.

    :return: A new class suitable as a metaclass for the actual model form.
             Therefore, it should be passed as the ``meta`` argument to
             :func:`model_form_factory`.

    Example usage:

    .. code-block:: python

        from wtforms.form import FormMeta


        class MyModelFormMeta(FormMeta):
            # do some metaclass magic here
            pass

        ModelFormMeta = model_form_meta_factory(MyModelFormMeta)
        ModelForm = model_form_factory(meta=ModelFormMeta)
    """

    class ModelFormMeta(base):
        """
        Meta class that overrides WTForms base meta class. The primary purpose
        of this class is allowing ModelForms use special configuration params
        under the 'Meta' class namespace.

        ModelForm classes inherit parent's Meta class properties.
        """

        def __init__(cls, *args, **kwargs):
            bases = []
            for class_ in cls.__mro__:
                if "Meta" in class_.__dict__:
                    bases.append(getattr(class_, "Meta"))

            if object not in bases:
                bases.append(object)

            cls.Meta = type("Meta", tuple(bases), {})

            base.__init__(cls, *args, **kwargs)

            if hasattr(cls.Meta, "model") and cls.Meta.model:
                generator = cls.Meta.form_generator(cls)
                generator.create_form(cls)

    return ModelFormMeta


ModelFormMeta = model_form_meta_factory()


def model_form_factory(base=Form, meta=ModelFormMeta, **defaults):
    """
    Create a base class for all model forms to derive from.

    :param base: Class that should be used as a base for the returned class.
                 By default, this is WTForms's base class
                 :class:`wtforms.Form`.

    :param meta: A metaclass to use on this class. Normally, you do not need to
                 provide this value, but if you want, you should check out
                 :func:`model_form_meta_factory`.

    :return: A class to be used as the base class for all forms that should be
             connected to a SQLAlchemy model class.

    Additional arguments provided to the form override the default
    configuration as described in :ref:`custom_base`.
    """

    class ModelForm(base, metaclass=meta):
        """
        Standard base-class for all forms to be combined with a model. Use
        :func:`model_form_factory` in case you wish to change its behavior.

        ``get_session``: If you want to use the Unique validator, you should
        define this method. If you are using Flask-SQLAlchemy along with
        WTForms-Alchemy you don't need to set this. If you define this in the
        superclass, it will not be overriden.
        """

        if not hasattr(base, "get_session"):
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
            skip_unknown_types = defaults.pop("skip_unknown_types", False)

            #: Whether or not to assign all fields as optional, useful when
            #: creating update forms for patch requests
            all_fields_optional = defaults.pop("all_fields_optional", False)

            validators = defaults.pop("validators", {})

            #: A dict with keys as field names and values as field arguments.
            field_args = defaults.pop("field_args", {})

            #: A dict with keys as field names and values as widget options.
            widget_options = defaults.pop("widget_options", {})

            #: Whether or not to include only indexed fields.
            only_indexed_fields = defaults.pop("only_indexed_fields", False)

            #: Whether or not to include primary keys.
            include_primary_keys = defaults.pop("include_primary_keys", False)

            #: Whether or not to include foreign keys. By default this is False
            #: indicating that foreign keys are not included in the generated
            #: form.
            include_foreign_keys = defaults.pop("include_foreign_keys", False)

            #: Whether or not to strip string fields
            strip_string_fields = defaults.pop("strip_string_fields", False)

            #: Whether or not to include datetime columns that have a default
            #: value. A good example is created_at column which has a default
            #: value of datetime.utcnow.
            include_datetimes_with_default = defaults.pop(
                "include_datetimes_with_default", False
            )

            #: The default validator to be used for not nullable columns. Set
            #: this to `None` if you wish to disable it.
            not_null_validator = defaults.pop("not_null_validator", InputRequired())

            #: A dictionary that overrides not null validation on type level.
            #: Keys should be valid SQLAlchemy types and values should be valid
            #: WTForms validators.
            not_null_validator_type_map = defaults.pop(
                "not_null_validator_type_map",
                ClassMap([(sa.String, [InputRequired(), DataRequired()])]),
            )

            #: Default email validator
            email_validator = defaults.pop("email_validator", Email)

            #: Default length validator
            length_validator = defaults.pop("length_validator", Length)

            #: Default unique validator
            unique_validator = defaults.pop("unique_validator", Unique)

            #: Default number range validator
            number_range_validator = defaults.pop("number_range_validator", NumberRange)

            #: Default date range validator
            date_range_validator = defaults.pop("date_range_validator", DateRange)

            #: Default time range validator
            time_range_validator = defaults.pop("time_range_validator", TimeRange)

            #: Default optional validator
            optional_validator = defaults.pop("optional_validator", Optional)

            #: Default URL validator
            url_validator = defaults.pop("url_validator", URL)

            #: Which form generator to use. Only override this if you have a
            #: valid form generator which you want to use instead of the
            #: default one.
            form_generator = defaults.pop("form_generator", FormGenerator)

            #: Default date format
            date_format = defaults.pop("date_format", "%Y-%m-%d")

            #: Default datetime format
            datetime_format = defaults.pop("datetime_format", "%Y-%m-%d %H:%M:%S")

            #: Dictionary of SQLAlchemy types as keys and WTForms field classes
            #: as values. The key value pairs of this dictionary override
            #: the key value pairs of FormGenerator.TYPE_MAP.
            #:
            #: Using this configuration option one can easily configure the
            #: type conversion in class level.
            type_map = defaults.pop("type_map", ClassMap())

            #: Whether or not to raise InvalidAttributExceptions when invalid
            #: attribute names are given for include / exclude or only
            attr_errors = defaults.pop("attr_errors", True)

            #: Additional fields to include in the generated form.
            include = defaults.pop("include", [])

            #: List of fields to exclude from the generated form.
            exclude = defaults.pop("exclude", [])

            #: List of fields to only include in the generated form.
            only = defaults.pop("only", [])

        def __init__(self, *args, **kwargs):
            """Sets object as form attribute."""

            self._obj = kwargs.get("obj", None)
            super().__init__(*args, **kwargs)

    if defaults:
        raise UnknownConfigurationOption(list(defaults.keys())[0])

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
