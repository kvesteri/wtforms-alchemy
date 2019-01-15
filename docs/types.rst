Type specific conversion
========================


Numeric type
------------

WTForms-Alchemy automatically converts Numeric columns to DecimalFields. The
converter is also smart enough to convert different decimal scales to
appropriate HTML5 input step args.


::


    class Account(Base):
        __tablename__ = 'event'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        balance = sa.Column(
            sa.Numeric(scale=2),
            nullable=False
        )

    class AccountForm(ModelForm):
        class Meta:
            model = Account


Now rendering AccountForm.balance would return the following HTML:

<input type='decimal' required step="0.01">


Arrow type
----------

WTForms-Alchemy supports the ArrowType of SQLAlchemy-Utils and converts it to
HTML5 compatible DateTimeField of WTForms-Components.

::


    from sqlalchemy_utils import ArrowType


    class Event(Base):
        __tablename__ = 'event'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        start_time = sa.Column(
            ArrowType(),
            nullable=False
        )

    class EventForm(ModelForm):
        class Meta:
            model = Event


Now the EventForm is essentially the same as:

::


    class EventForm(Form):
        start_time = DateTimeField(validators=[DataRequired()])


Choice type
-----------

WTForms-Alchemy automatically converts
:class:`sqlalchemy_utils.types.choice.ChoiceType` to WTForms-Components
SelectField.


::


    from sqlalchemy_utils import ChoiceType


    class Event(Base):
        __tablename__ = 'event'
        TYPES = [
            (u'party', u'Party'),
            (u'training, u'Training')
        ]

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        type = sa.Column(ChoiceType(TYPES))


    class EventForm(ModelForm):
        class Meta:
            model = Event


Now the EventForm is essentially the same as:

::

    from wtforms_alchemy.utils import choice_type_coerce_factory


    class EventForm(Form):
        type = SelectField(
            choices=Event.TYPES,
            coerce=choice_type_coerce_factory(Event.type.type),
            validators=[DataRequired()]
        )



Color type
----------

::


    from sqlalchemy_utils import ColorType


    class CustomView(Base):
        __tablename__ = 'view'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        background_color = sa.Column(
            ColorType(),
            nullable=False
        )

    class CustomViewForm(ModelForm):
        class Meta:
            model = CustomView


Now the CustomViewForm is essentially the same as:

::


    from wtforms_components import ColorField


    class CustomViewForm(Form):
        color = ColorField(validators=[DataRequired()])



Country type
------------

::


    from sqlalchemy_utils import CountryType


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        country = sa.Column(CountryType, nullable=False)


    class UserForm(ModelForm):
        class Meta:
            model = User


The UserForm is essentially the same as:

::


    from wtforms_components import CountryField


    class UserForm(Form):
        country = CountryField(validators=[DataRequired()])



Email type
----------

::


    from sqlalchemy_utils import EmailType


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        email = sa.Column(EmailType, nullable=False)


    class UserForm(ModelForm):
        class Meta:
            model = User


The good old wtforms equivalent of this form would be:

::


    from wtforms_components import EmailField


    class UserForm(Form):
        email = EmailField(validators=[DataRequired()])



Password type
-------------

Consider the following model definition:

::


    from sqlalchemy_utils import PasswordType


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        name = sa.Column(sa.Unicode(100), nullable=False)
        password = sa.Column(
            PasswordType(
                schemes=['pbkdf2_sha512']
            ),
            nullable=False
        )

    class UserForm(ModelForm):
        class Meta:
            model = User


Now the UserForm is essentially the same as:

::

    class UserForm(Form):
        name = TextField(validators=[DataRequired(), Length(max=100)])
        password = PasswordField(validators=[DataRequired()])




Phonenumber type
----------------

WTForms-Alchemy supports the PhoneNumberType of SQLAlchemy-Utils and converts it automatically
to WTForms-Components PhoneNumberField. This field renders itself as HTML5 compatible phonenumber input.


Consider the following model definition:

::


    from sqlalchemy_utils import PhoneNumberType


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        name = sa.Column(sa.Unicode(100), nullable=False)
        phone_number = sa.Column(PhoneNumberType())


    class UserForm(ModelForm):
        class Meta:
            model = User


Now the UserForm is essentially the same as:

::

    from wtforms_components import PhoneNumberField


    class UserForm(Form):
        name = TextField(validators=[DataRequired(), Length(max=100)])
        phone_number = PhoneNumberField(validators=[DataRequired()])


URL type
--------

WTForms-Alchemy automatically converts SQLAlchemy-Utils URLType to StringField and adds URL validator for it.

Consider the following model definition:

::


    from sqlalchemy_utils import URLType


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        website = sa.Column(URLType())


    class UserForm(ModelForm):
        class Meta:
            model = User


Now the UserForm is essentially the same as:

::

    from wtforms_components import StringField
    from wtforms.validators import URL


    class UserForm(Form):
        website = StringField(validators=[URL()])
