from collections import Iterable, Mapping

import six
from sqlalchemy import Column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from wtforms import ValidationError


class Unique(object):
    """Checks field values unicity against specified table fields.

    :param column:
        InstrumentedAttribute object, eg. User.name, or
        Column object, eg. user.c.name, or
        a field name, eg. 'name' or
        a tuple of InstrumentedAttributes, eg. (User.name, User.email) or
        a dictionary mapping field names to InstrumentedAttributes, eg.
        {
            'name': User.name,
            'email': User.email
        }
    :param get_session:
        A function that returns a SQAlchemy Session. This parameter is not
        needed if the given model supports Flask-SQLAlchemy styled query
        parameter.
    :param message:
        The error message.
    """
    field_flags = ('unique', )

    def __init__(self, column, get_session=None, message=None):
        self.column = column
        self.message = message
        self.get_session = get_session

    @property
    def query(self):
        self._check_for_session(self.model)
        if self.get_session:
            return self.get_session().query(self.model)
        elif hasattr(self.model, 'query'):
            return getattr(self.model, 'query')
        else:
            raise Exception(
                'Validator requires either get_session or Flask-SQLAlchemy'
                ' styled query parameter'
            )

    def _check_for_session(self, model):
        if not hasattr(model, 'query') and not self.get_session:
            raise Exception('Could not obtain SQLAlchemy session.')

    def _syntaxes_as_tuples(self, form, field, column):
        """Converts a set of different syntaxes into a tuple of tuples"""
        if isinstance(column, six.string_types):
            return ((column, getattr(form.Meta.model, column)),)
        elif isinstance(column, Mapping):
            return tuple(
                (x[0], self._syntaxes_as_tuples(form, field, x[1])[0][1])
                for x in column.items()
            )
        elif isinstance(column, Iterable):
            return tuple(
                self._syntaxes_as_tuples(form, field, x)[0]
                for x in column
            )
        elif isinstance(column, (Column, InstrumentedAttribute)):
            return ((column.key, column),)
        else:
            raise TypeError("Invalid syntax for column")

    def __call__(self, form, field):
        columns = self._syntaxes_as_tuples(form, field, self.column)
        self.model = columns[0][1].class_
        query = self.query
        for field_name, column in columns:
            query = query.filter(column == form[field_name].data)
        obj = query.first()

        if not hasattr(form, '_obj'):
            raise Exception(
                "Couldn't access Form._obj attribute. Either make your form "
                "inherit WTForms-Alchemy ModelForm or WTForms-Components "
                "ModelForm or make this attribute available in your form."
            )

        if obj and not form._obj == obj:
            if self.message is None:
                self.message = field.gettext(u'Already exists.')
            raise ValidationError(self.message)
