from wtforms import ValidationError
from sqlalchemy.orm.exc import NoResultFound


class DateRange(object):
    """
    Same as wtforms.validators.NumberRange but validates date.
    """
    date_greater_than = u'Date must be greater than %(min)s.'

    date_less_than = u'Date must be less than %(max)s.'

    date_between = u'Date must be between %(min)s and %(max)s.'

    def __init__(self, min=None, max=None, format='%Y-%m-%d', message=None):
        self.min = min
        self.max = max
        self.format = format
        self.message = message

    def __call__(self, form, field):
        data = field.data
        min_ = self.min() if callable(self.min) else self.min
        max_ = self.max() if callable(self.max) else self.max
        if (data is None or (min_ is not None and data < min_) or
                (max_ is not None and data > max_)):
            if self.message is None:
                if max_ is None:
                    self.message = field.gettext(self.date_greater_than)
                elif min_ is None:
                    self.message = field.gettext(self.date_less_than)
                else:
                    self.message = field.gettext(self.date_between)

            raise ValidationError(
                self.message % dict(
                    field_label=field.label,
                    min=min_.strftime(self.format) if min_ else '',
                    max=max_.strftime(self.format) if max_ else ''
                )
            )


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
