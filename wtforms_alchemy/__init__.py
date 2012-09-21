#import pytz
from wtforms import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FloatField,
    Form,
    IntegerField,
    TextAreaField,
    TextField,
    SelectField as _SelectField,
)
from wtforms.form import FormMeta
from wtforms.validators import (
    Length,
    Optional,
    NumberRange,
    Required,
    ValidationError
)
from sqlalchemy import types
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.exc import NoResultFound


class Unique(object):
    """Checks field value unicity against specified table field.

    Currently only supports Flask-SQLAlchemy style models which have the query
    class.

    We must require models to have query class so that unique validators can be
    generated without the need of explicitly setting the SQLAlchemy session.

    :param model:
        The model to check unicity against.
    :param column:
        The unique column.
    :param message:
        The error message.
    """
    field_flags = ('unique', )

    def __init__(self, model, column, message=None):
        self.model = model
        self.column = column
        self.message = message

        if not hasattr(self.model, 'query'):
            raise Exception('Model classes must have query class.')

    def __call__(self, form, field):
        try:
            obj = (
                self.model.query
                .filter(self.column == field.data).one()
            )

            if not hasattr(form, '_obj') or not form._obj == obj:
                if self.message is None:
                    self.message = field.gettext(u'Already exists.')
                raise ValidationError(self.message)
        except NoResultFound:
            pass


def is_scalar(value):
    return isinstance(value, (type(None), str, int, float, bool, unicode))


def null_or_unicode(value):
    return unicode(value) or None


class SelectField(_SelectField):
    def pre_validate(self, form):
        if self.data is None and u'' in [v[0] for v in self.choices]:
            return True

        _SelectField.pre_validate(self, form)


class UnknownTypeException(Exception):
    pass


class FormGenerator(object):
    TYPE_MAP = {
        types.BigInteger: IntegerField,
        types.SmallInteger: IntegerField,
        types.Integer: IntegerField,
        types.DateTime: DateTimeField,
        types.Date: DateField,
        types.Text: TextAreaField,
        types.Unicode: TextField,
        types.UnicodeText: TextAreaField,
        types.Float: FloatField,
        types.Numeric: DecimalField,
        types.Boolean: BooleanField,
        types.Enum: SelectField,
    }

    def __init__(self, model_class, meta):
        self.model_class = model_class
        self.meta = meta

    def create_form(self, form):
        fields = set(self.model_class._sa_class_manager.values())
        tmp = []
        for field in fields:
            column = field.property
            if isinstance(column, ColumnProperty) and self.skip_column(column):
                continue
            tmp.append(field)
        fields = set(tmp)

        if self.meta.only:
            fields = set([
                getattr(self.model_class, field)
                for field in self.meta.only
            ])
        else:
            if self.meta.include:
                fields.update(set([
                    getattr(self.model_class, field)
                    for field in self.meta.include
                ]))

            if self.meta.exclude:
                func = lambda a: a.key not in self.meta.exclude
                fields = filter(func, fields)

        return self.create_fields(form, fields)

    def create_fields(self, form, fields):
        for field in fields:
            column = field.property

            if not isinstance(column, ColumnProperty):
                continue

            name = column.columns[0].name
            form_field = self.create_field(column)

            if not hasattr(form, name):
                setattr(form, name, form_field)
        return form

    def skip_column(self, column_property):
        """Whether or not to skip column in the generation process."""
        column = column_property.columns[0]
        if (not self.meta.include_primary_keys and column.primary_key or
                column.foreign_keys):
            return True

        if column_property._is_polymorphic_discriminator:
            return True

        if (not self.meta.include_datetimes_with_default and
                isinstance(column.type, types.DateTime) and
                column.default):
            return True

        if self.meta.only_indexed_fields and not self.has_index(column):
            return True
        return False

    def has_index(self, column):
        """Whether or not this column has an index."""
        if column.primary_key or column.foreign_keys:
            return True
        table = column.table
        for index in table.indexes:
            if len(index.columns) == 1 and column.name in index.columns:
                return True
        return False

    def create_field(self, column_property):
        column = column_property.columns[0]
        name = column.name
        validators = []
        kwargs = {}
        field_class = self.get_field_class(column)

        if self.meta.all_fields_optional:
            validators.append(Optional())
        else:
            if column.default and is_scalar(column.default.arg):
                kwargs['default'] = column.default.arg
            else:
                if not column.nullable:
                    kwargs['default'] = self.meta.default

                if not column.nullable and self.meta.assign_required:
                    validators.append(Required())

        validators.extend(self.create_validators(column))
        kwargs['validators'] = validators

        if 'description' in column.info:
            kwargs['description'] = column.info['description']

        if 'label' in column.info:
            kwargs['label'] = column.info['label']
        else:
            kwargs['label'] = name

        min_ = column.info['min'] if 'min' in column.info else None
        max_ = column.info['max'] if 'max' in column.info else None

        if min_ or max_:
            validators.append(NumberRange(min=min_, max=max_))

        if hasattr(column.type, 'enums') or 'choices' in column.info:
            if column.nullable:
                kwargs['coerce'] = null_or_unicode

            if 'choices' in column.info and column.info['choices']:
                kwargs['choices'] = column.info['choices']
            else:
                kwargs['choices'] = [
                    (enum, enum) for enum in column.type.enums
                ]

        if isinstance(column.type, types.DateTime):
            kwargs['format'] = self.meta.datetime_format

        if isinstance(column.type, types.Date):
            kwargs['format'] = self.meta.date_format

        return field_class(**kwargs)

    def create_validators(self, column):
        validators = []
        validator = self.length_validator(column)
        if validator:
            validators.append(validator)
        name = column.name
        if name in self.meta.validators:
            if isinstance(self.meta.validators[name], list):
                validators.extend(self.meta.validators[name])
            else:
                validators.append(self.meta.validators[name])

        if column.unique:
            validators.append(
                Unique(
                    self.model_class,
                    getattr(self.model_class, name)
                )
            )
        if 'validators' in column.info and column.info['validators']:
            try:
                validators.extend(column.info['validators'])
            except TypeError:
                validators.append(column.info['validators'])
        return validators

    def length_validator(self, column):
        """
        Returns colander length validator for given column
        """
        if hasattr(column.type, 'length') and column.type.length:
            return Length(max=column.type.length)

    def get_field_class(self, column):
        """
        Returns WTForms field class that corresponds to given SQLAlchemy column
        type.
        """
        if 'choices' in column.info:
            return SelectField
        for class_ in self.TYPE_MAP:
            # Float type in sqlalchemy inherits numeric type, hence we need
            # the following check
            if column.type.__class__ is types.Float:
                if isinstance(column.type, types.Float):
                    return self.TYPE_MAP[types.Float]
            if isinstance(column.type, class_):
                return self.TYPE_MAP[class_]
        raise UnknownTypeException(column.type)


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
            generator = cls.Meta.form_generator(cls.Meta.model, cls.Meta)
            generator.create_form(cls)

        return FormMeta.__call__(cls, *args, **kwargs)


def model_form_factory(base=Form):
    """Creates new model form, with given base class."""

    class ModelForm(base):
        __metaclass__ = ModelFormMeta

        class Meta:
            model = None

            default = None

            #: Whether or not to assign non-nullable fields as required
            assign_required = True

            #: Whether or not to assign all fields as optional, useful when
            #: creating update forms
            all_fields_optional = False

            validators = {}

            #: Whether or not to include only indexed fields
            only_indexed_fields = False

            #: Whether or not to include primary keys.
            include_primary_keys = False

            #: Whether or not to include primary keys. By default this is False
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
