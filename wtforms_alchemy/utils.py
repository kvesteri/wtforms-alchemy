from sqlalchemy import types


def is_scalar(value):
    return isinstance(value, (type(None), str, int, float, bool, unicode))


def null_or_unicode(value):
    return unicode(value) or None


def null_or_int(value):
    try:
        return int(value)
    except TypeError:
        return None


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
