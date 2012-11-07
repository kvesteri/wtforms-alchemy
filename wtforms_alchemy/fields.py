import time
from datetime import datetime
from cgi import escape
from wtforms import widgets, Form
from wtforms.fields import (
    Field,
    DateField,
    FormField,
    SelectField as _SelectField,
)
from wtforms.fields.core import _unset_value
from wtforms.validators import ValidationError, DataRequired
from wtforms.widgets import (
    HTMLString, html_params, Select as BaseSelectWidget
)


class SelectWidget(BaseSelectWidget):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """
    @classmethod
    def render_option(cls, value, label, mixed):
        """
        Render option as HTML tag, but not forget to wrap options into
        ``optgroup`` tag if ``label`` var is ``list`` or ``tuple``.
        """
        if isinstance(label, (list, tuple)):
            children = []

            for item_value, item_label in label:
                item_html = cls.render_option(item_value, item_label, mixed)
                children.append(item_html)

            html = u'<optgroup label="%s">%s</optgroup>'
            data = (escape(unicode(value)), u'\n'.join(children))
        else:
            coerce_func, data = mixed
            if isinstance(data, list) or isinstance(data, tuple):
                selected = coerce_func(value) in data
            else:
                selected = coerce_func(value) == data

            options = {'value': value}

            if selected:
                options['selected'] = u'selected'

            html = u'<option %s>%s</option>'
            data = (html_params(**options), escape(unicode(label)))

        return HTMLString(html % data)


class SelectField(_SelectField):
    """
    Add support of ``optgorup``'s' to default WTForms' ``SelectField`` class.

    So, next choices would be supported as well::

        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            ))
        )

    Also supports lazy choices (callables that return an iterable)
    """
    widget = SelectWidget()

    def iter_choices(self):
        """
        We should update how choices are iter to make sure that value from
        internal list or tuple should be selected.
        """
        for value, label in self.concrete_choices:
            yield (value, label, (self.coerce, self.data))

    @property
    def concrete_choices(self):
        if callable(self.choices):
            return self.choices()
        return self.choices

    @property
    def choice_values(self):
        values = []
        for value, label in self.concrete_choices:
            if isinstance(label, (list, tuple)):
                for subvalue, sublabel in label:
                    values.append(subvalue)
            else:
                values.append(value)
        return values

    def pre_validate(self, form):
        """
        Don't forget to validate also values from embedded lists.
        """
        values = self.choice_values
        if self.data is None and u'' in values:
            return True

        if self.data in values:
            return True

        raise ValidationError(self.gettext(u'Not a valid choice'))


class SelectMultipleField(SelectField):
    """
    No different from a normal select field, except this one can take (and
    validate) multiple choices.  You'll need to specify the HTML `rows`
    attribute to the select field when rendering.
    """
    widget = SelectWidget(multiple=True)

    def process_data(self, value):
        try:
            self.data = list(self.coerce(v) for v in value)
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        try:
            self.data = list(self.coerce(x) for x in valuelist)
        except ValueError:
            raise ValueError(
                self.gettext(
                    'Invalid choice(s): one or more data'
                    ' inputs could not be coerced'
                )
            )

    def pre_validate(self, form):
        if self.data:
            values = self.choice_values
            for value in self.data:
                if value not in values:
                    raise ValueError(
                        self.gettext(
                            "'%(value)s' is not a valid"
                            " choice for this field"
                        ) % dict(value=value)
                    )


class TimeField(Field):
    """
    A text field which stores a `datetime.time` matching a format.
    """
    widget = widgets.TextInput()

    def __init__(self, label=None, validators=None, format='%H:%M', **kwargs):
        super(TimeField, self).__init__(label, validators, **kwargs)
        self.format = format

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            time_str = ' '.join(valuelist)
            try:
                self.data = time.strptime(time_str, self.format)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid datetime value'))


class Date():
    date = None
    time = None


class SplitDateTimeField(FormField):
    def __init__(self, label=None, validators=None, separator='-', **kwargs):
        FormField.__init__(
            self,
            DateTimeForm,
            label=label,
            validators=validators,
            separator=separator,
            **kwargs
        )

    def process(self, formdata, data=_unset_value):
        if data is _unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default
        if data:
            obj = Date()
            obj.date = data.date()
            obj.time = data.time()
        else:
            obj = None
        FormField.process(self, formdata, data=obj)

    def populate_obj(self, obj, name):
        if hasattr(obj, name):
            date = self.date.data
            hours, minutes = self.time.data.tm_hour, self.time.data.tm_min
            setattr(obj, name, datetime(
                date.year, date.month, date.day, hours, minutes
            ))


class DateTimeForm(Form):
    date = DateField(u'Date', validators=[DataRequired()])
    time = TimeField(u'Time', validators=[DataRequired()])
