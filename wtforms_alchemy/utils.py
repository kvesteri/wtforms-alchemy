import six
import sqlalchemy as sa
from sqlalchemy import types
from .exc import UnknownIdentityException


def strip_string(value):
    if isinstance(value, six.string_types):
        return value.strip()
    return value


def is_scalar(value):
    return isinstance(value, (type(None), six.text_type, int, float, bool))


def null_or_unicode(value):
    return six.text_type(value) or None


def null_or_int(value):
    try:
        return int(value)
    except TypeError:
        return None


def is_numerical_column(column):
    return (
        is_integer_column(column) or
        isinstance(column.type, types.Float) or
        isinstance(column.type, types.Numeric)
    )


def is_integer_column(column):
    return (
        isinstance(column.type, types.Integer) or
        isinstance(column.type, types.SmallInteger) or
        isinstance(column.type, types.BigInteger)
    )


def is_date_column(column):
    return (
        isinstance(column.type, types.Date) or
        isinstance(column.type, types.DateTime)
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


def table(model):
    if isinstance(model, sa.schema.Table):
        return model
    else:
        return model.__table__


def primary_keys(model):
    for column in table(model).c:
        if column.primary_key:
            yield column


def has_entity(obj, name, model, data):
    for column in primary_keys(model):
        if not column.name in data or not data[column.name]:
            return False

        found = False
        coerce_func = column.type.python_type
        for related_obj in getattr(obj, name):
            value = getattr(related_obj, column.name)

            try:
                if value == coerce_func(data[column.name]):
                    found = True
            except ValueError:
                # coerce failed
                pass

        if not found:
            raise UnknownIdentityException()
    return True
