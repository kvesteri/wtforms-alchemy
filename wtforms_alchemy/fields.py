from cgi import escape
from wtforms.fields import SelectField as _SelectField
from wtforms.validators import ValidationError
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

    """
    widget = SelectWidget()

    def iter_choices(self):
        """
        We should update how choices are iter to make sure that value from
        internal list or tuple should be selected.
        """
        for value, label in self.choices:
            yield (value, label, (self.coerce, self.data))

    @property
    def choice_values(self):
        values = []
        for value, label in self.choices:
            if isinstance(label, (list, tuple)):
                for subvalue, sublabel in label:
                    values.append(subvalue)
            else:
                values.append(value)
        return values

    def pre_validate(self, form, choices=None):
        """
        Don't forget to validate also values from embedded lists.
        """
        if self.data is None and u'' in [v[0] for v in self.choices]:
            return True

        default_choices = choices is None
        choices = choices or self.choices

        for value, label in choices:
            found = False

            if isinstance(label, (list, tuple)):
                found = self.pre_validate(form, label)

            if found or value == self.data:
                return True

        if not default_choices:
            return False

        raise ValidationError(self.gettext(u'Not a valid choice'))


class SelectMultipleField(SelectField):
    """
    No different from a normal select field, except this one can take (and
    validate) multiple choices.  You'll need to specify the HTML `rows`
    attribute to the select field when rendering.
    """
    widget = SelectWidget(multiple=True)

    # def iter_choices(self):
    #     """
    #     We should update how choices are iter to make sure that value from
    #     internal list or tuple should be selected.
    #     """
    #     for value, label in self.choices:
    #         yield (value, label, (self.coerce, self.data))

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
