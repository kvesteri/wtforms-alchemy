from wtforms import ValidationError
from wtforms.validators import StopValidation
from sqlalchemy.orm.exc import NoResultFound


class ControlStructure(object):
    """
    Base object for validator control structures
    """

    message = None

    def reraise(self, exc):
        if not self.message:
            raise exc
        else:
            raise type(exc)(self.message)


class Chain(ControlStructure):
    """
    Represents a chain of validators, useful when using multiple validators
    with If control structure.

    :param validators:
        list of validator objects
    :param message:
        custom validation error message, if this message is set and some of the
        child validators raise a ValidationError, an exception is being raised
        again with this custom message.
    """
    def __init__(self, validators, message=None):
        self.validators = validators
        if message:
            self.message = message

    def __call__(self, form, field):
        for validator in self.validators:
            try:
                validator(form, field)
            except ValidationError, exc:
                self.reraise(exc)
            except StopValidation, exc:
                self.reraise(exc)


class If(ControlStructure):
    """
    Conditional validator.

    :param condition: callable which takes two arguments form and field
    :param validator: encapsulated validator, this validator is validated
                      only if given condition returns true
    :param message: custom message, which overrides child validator's
                    validation error message
    """
    def __init__(self, condition, validator, message=None):
        self.condition = condition
        self.validator = validator

        if message:
            self.message = message

    def __call__(self, form, field):
        if self.condition(form, field):
            try:
                self.validator(form, field)
            except ValidationError, exc:
                self.reraise(exc)
            except StopValidation, exc:
                self.reraise(exc)


class DateRange(object):
    """
    Same as wtforms.validators.NumberRange but validates date.

    :param min:
        The minimum required value of the date. If not provided, minimum
        value will not be checked.
    :param max:
        The maximum value of the date. If not provided, maximum value
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)s` and `%(max)s` if desired. Useful defaults
        are provided depending on the existence of min and max.
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
