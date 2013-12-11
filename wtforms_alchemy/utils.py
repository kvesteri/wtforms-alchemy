import six
import sqlalchemy as sa
from sqlalchemy import types


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


def flatten(list_):
    result = []
    if isinstance(list_, list):
        for value in list_:
            result.extend(flatten(value))
    else:
        result.append(list_)
    return result


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


def table(model):
    if isinstance(model, sa.schema.Table):
        return model
    else:
        return model.__table__


def primary_keys(model):
    for column in table(model).c:
        if column.primary_key:
            yield column


def find_entity(coll, model, data):
    for column in primary_keys(model):
        if not column.name in data or not data[column.name]:
            return None
        coerce_func = column.type.python_type
        for related_obj in coll:
            value = getattr(related_obj, column.name)

            try:
                if value == coerce_func(data[column.name]):
                    return related_obj
            except ValueError:
                # coerce failed
                pass
    return None
