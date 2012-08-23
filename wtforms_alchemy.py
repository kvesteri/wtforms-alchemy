import inspect

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
)
from wtforms.form import FormMeta
from wtforms.validators import Length, Required
from sqlalchemy import types
from sqlalchemy.orm.properties import RelationshipProperty, ColumnProperty


class Null(object):
    pass


null = Null()


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
    }

    def __init__(self,
                 model_class,
                 default=None,
                 assign_defaults=True,
                 validator=None,
                 only_indexed_fields=False,
                 include_primary_keys=False,
                 include_foreign_keys=False,
                 include_relations=True):
        self.validator = validator
        self.model_class = model_class
        self.default = default
        self.assign_defaults = assign_defaults
        self.only_indexed_fields = only_indexed_fields
        self.include_primary_keys = include_primary_keys
        self.include_foreign_keys = include_foreign_keys
        self.include_relations = include_relations

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

    def create_fields(self, form, fields, include_relations=True):
        for field in fields:
            column = field.property

            form_field = None
            if isinstance(column, RelationshipProperty):
                # if include_relations:
                #     form_field = self.relation_field(column)
                #     name = column.key
                pass
            elif isinstance(column, ColumnProperty):
                name = column.columns[0].name
                form_field = self.column_schema_node(column)
            if not form_field:
                continue
            if not hasattr(form, name):
                setattr(form, name, form_field)
        return form

    def is_nullable(self, name):
        return True

    def is_read_only(self, name):
        return False

    def validators(self, name):
        return None

    def relation_field(self, relation_property):
        model = relation_property.argument
        if model.__class__.__name__ == 'function':
            # for string based relations (relations where the first
            # argument is a classname string instead of actual class)
            # sqlalchemy generates return_cls functions which we need
            # to call in order to obtain the actual model class
            model = model()

        name = relation_property.key

        if name not in self.model_class.__form__:
            return None

        if not inspect.isclass(model) or \
                not issubclass(model, FormMixin):
            raise Exception('Could not create schema for %r' % model)
        else:
            if self.is_nullable(name):
                default = null
            else:
                default = self.missing
            kwargs = {
                'default': default,
                'assign_defaults': self.assign_defaults
            }
            try:
                form_creator = self.model_class.__form__[name]['schema']
            except KeyError:
                form_creator = model.get_form
                del kwargs['assign_defaults']

            form = form_creator(**kwargs)
            # if self.is_nullable(name):
            #     schema_node = nullable(schema_node)
            return form

    def skip_column(self, column_property):
        column = column_property.columns[0]
        if (not self.include_primary_keys and column.primary_key or
                column.foreign_keys):
            return True

        if (self.is_read_only(column.name) or
                column_property._is_polymorphic_discriminator):
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

    def column_schema_node(self, column_property):
        column = column_property.columns[0]
        name = column.name
        validators = []

        field_class = self.get_field_class(column.type)
        if column.default and self.assign_defaults:
            default = column.default.arg
        else:
            if self.is_nullable(name) and column.nullable:
                default = null
            else:
                default = self.default
                validators.append(Required())

        validators.append(self.length_validator(column))
        return field_class(
            name,
            default=default,
            validators=validators
        )

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
    return {name: getattr(cls, name) for name in dir(cls)}


class ModelFormMeta(FormMeta):
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
                assign_defaults=cls.Meta.assign_defaults,
                validator=cls.Meta.validator,
                only_indexed_fields=cls.Meta.only_indexed_fields,
                include_primary_keys=cls.Meta.include_primary_keys,
                include_foreign_keys=cls.Meta.include_foreign_keys,
                include_relations=cls.Meta.include_relations
            )
            generator.create_form(cls, cls.Meta.include, cls.Meta.exclude)

        return FormMeta.__call__(cls, *args, **kwargs)


class ModelForm(Form):
    __metaclass__ = ModelFormMeta

    class Meta:
        model = None
        default = None
        assign_defaults = True
        validator = None
        only_indexed_fields = False
        include_primary_keys = False
        include_foreign_keys = False
        include_relations = False
        form_generator = FormGenerator
        include = []
        exclude = []

    def __init__(self, *args, **kwargs):
        """Sets object as form attribute."""

        if 'obj' in kwargs:
            self._obj = kwargs['obj']
        super(ModelForm, self).__init__(*args, **kwargs)


class ModelCreateForm(ModelForm):
    class Meta:
        assign_defaults = True


class ModelUpdateForm(ModelForm):
    class Meta:
        default = null


class ModelSearchForm(ModelForm):
    class Meta:
        only_indexed_fields = True
        include_primary_keys = True
