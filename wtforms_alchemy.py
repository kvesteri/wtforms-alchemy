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
    SelectField,
)
from wtforms.form import FormMeta
from wtforms.validators import Length, Required, ValidationError
from sqlalchemy import types
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.exc import NoResultFound


class Null(object):
    pass


null = Null()


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

    def __init__(self,
                 model_class,
                 default=None,
                 assign_required=True,
                 validator=None,
                 only_indexed_fields=False,
                 include_primary_keys=False,
                 include_foreign_keys=False):
        self.validator = validator
        self.model_class = model_class
        self.default = default
        self.assign_required = assign_required
        self.only_indexed_fields = only_indexed_fields
        self.include_primary_keys = include_primary_keys
        self.include_foreign_keys = include_foreign_keys

    def create_form(self, form, include=None, exclude=None):
        fields = set(self.model_class._sa_class_manager.values())
        tmp = []
        for field in fields:
            column = field.property
            if isinstance(column, ColumnProperty) and self.skip_column(column):
                continue
            tmp.append(field)
        fields = set(tmp)

        if include:
            fields.update(set(
                [getattr(self.model_class, field) for field in include]
            ))

        if exclude:
            func = lambda a: a.key not in exclude
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
        if (not self.include_primary_keys and column.primary_key or
                column.foreign_keys):
            return True

        if column_property._is_polymorphic_discriminator:
            return True

        if self.only_indexed_fields and not self.has_index(column):
            return True
        return False

    def has_index(self, column):
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

        field_class = self.get_field_class(column.type)
        if column.default:
            default = column.default.arg
        else:
            if column.nullable:
                default = null
            else:
                default = self.default

        if not column.nullable and self.assign_required:
            validators.append(Required())
        validator = self.length_validator(column)
        if validator:
            validators.append(validator)

        if column.unique:
            validators.append(
                Unique(
                    self.model_class,
                    getattr(self.model_class, name)
                )
            )
        kwargs = {
            'validators': validators,
            'default': default,
        }
        if hasattr(column.type, 'enums'):
            kwargs['choices'] = [(enum, enum) for enum in column.type.enums]

        return field_class(name, **kwargs)

    def length_validator(self, column):
        """
        Returns colander length validator for given column
        """
        if hasattr(column.type, 'length') and column.type.length:
            return Length(max=column.type.length)

    def get_field_class(self, column_type):
        for class_ in self.TYPE_MAP:
            # Float type in sqlalchemy inherits numeric type, hence we need
            # the following check
            if column_type.__class__ is types.Float:
                if isinstance(column_type, types.Float):
                    return self.TYPE_MAP[types.Float]
            if isinstance(column_type, class_):
                return self.TYPE_MAP[class_]
        raise UnknownTypeException(column_type)


def class_list(cls):
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
            generator = cls.Meta.form_generator(
                model_class=cls.Meta.model,
                default=cls.Meta.default,
                assign_required=cls.Meta.assign_required,
                validator=cls.Meta.validator,
                only_indexed_fields=cls.Meta.only_indexed_fields,
                include_primary_keys=cls.Meta.include_primary_keys,
                include_foreign_keys=cls.Meta.include_foreign_keys,
            )
            generator.create_form(cls, cls.Meta.include, cls.Meta.exclude)

        return FormMeta.__call__(cls, *args, **kwargs)


class ModelForm(Form):
    __metaclass__ = ModelFormMeta

    class Meta:
        model = None
        default = None
        #: Whether or not to assign non-nullable fields as required
        assign_required = True
        validator = None
        #: Whether or not to include only indexed fields
        only_indexed_fields = False
        #: Whether or not to include primary keys.
        include_primary_keys = False
        #: Whether or not to include primary keys. By default this is False
        #: indicating that foreign keys are not included in the generated form.
        include_foreign_keys = False
        #: Which form generator to use. Only override this if you have a valid
        #: form generator which you want to use instead of the default one.
        form_generator = FormGenerator
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


class ModelCreateForm(ModelForm):
    pass


class ModelUpdateForm(ModelForm):
    class Meta:
        default = null
        assign_required = False


class ModelSearchForm(ModelForm):
    class Meta:
        only_indexed_fields = True
        include_primary_keys = True
