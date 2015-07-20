Validators
==========


Auto-assigned validators
------------------------

By default WTForms-Alchemy ModelForm assigns the following validators:
    * InputRequired validator if column is not nullable and has no default value
    * DataRequired validator if column is not nullable, has no default value and is of type `sqlalchemy.types.String`
    * NumberRange validator if column if of type Integer, Float or Decimal and column info parameter has min or max arguments defined
    * DateRange validator if column is of type Date or DateTime and column info parameter has min or max arguments defined
    * TimeRange validator if column is of type Time and info parameter has min or max arguments defined
    * Unique validator if column has a unique index
    * Length validator for String/Unicode columns with max length
    * Optional validator for all nullable columns


Unique validator
----------------

WTForms-Alchemy automatically assigns unique validators for columns which have unique indexes defined. Unique validator raises ValidationError exception whenever a non-unique value for given column is assigned. Consider the following model/form definition. Notice how you need to define get_session() classmethod for your form. Unique validator uses this method for getting the appropriate SQLAlchemy session.
::


    engine = create_engine('sqlite:///:memory:')

    Base = declarative_base()

    Session = sessionmaker(bind=engine)
    session = Session()


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(100), nullable=False)
        email = sa.Column(
            sa.Unicode(255),
            nullable=False,
            unique=True
        )

    class UserForm(ModelForm):
        class Meta:
            model = User

        @classmethod
        def get_session():
            # this method should return sqlalchemy session
            return session


Here UserForm would behave the same as the following form:
::


    class UserForm(Form):
        name = TextField('Name', validators=[DataRequired(), Length(max=100)])
        email = TextField(
            'Email',
            validators=[
                DataRequired(),
                Length(max=255),
                Unique(User.email, get_session=lambda: session)
            ]
        )


If you are using Flask-SQLAlchemy or similar tool, which assigns session-bound query property to your declarative models, you don't need to define the get_session() method. Simply use:

::

    Unique(User.email)


Using unique validator with existing objects
--------------------------------------------

When editing an existing object, WTForms-Alchemy must know the object currently edited to avoid raising a ValidationError. Here how to proceed to inform WTForms-Alchemy of this case.
Example::

    obj = MyModel.query.get(1)
    form = MyForm(obj=obj)
    form.populate_obj(obj)
    form.validate()

WTForms-Alchemy will then understand to avoid the unique validation of the object with this same object.


Range validators
----------------

WTForms-Alchemy automatically assigns range validators based on column type and assigned column info min and max attributes.

In the following example we create a form for Event model where start_time can't be set in the past.

::

    class Event(Base):
        __tablename__ = 'event'

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255))
        start_time = sa.Column(sa.DateTime, info={'min': datetime.now()})


    class EventForm(ModelForm):
        class Meta:
            model = Event



Additional field validators
---------------------------

Example::

    from wtforms.validators import Email

    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        email = sa.Column(
            sa.Unicode(255),
            nullable=False,
            info={'validators': Email()}
        )

    class UserForm(ModelForm):
        class Meta:
            model = User

Now the 'email' field of UserForm would have Email validator.


Overriding default validators
-----------------------------

Sometimes you may want to override what class WTForms-Alchemy uses for email, number_range, length etc. validations.
For all automatically assigned validators WTForms-Alchemy provides configuration options to override the default validator.

In the following example we set a custom Email validator for User class.

::


    from sqlalchemy_utils import EmailType
    from wtforms_components import Email


    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        email = sa.Column(
            EmailType,
            nullable=False,
        )

    class MyEmailValidator(Email):
        def __init__(self, message='My custom email error message'):
            Email.__init__(self, message=message)


    class UserForm(ModelForm):
        class Meta:
            model = User
            email_validator = MyEmailValidator


If you don't wish to subclass you can simply use functions / lambdas:

::


    def email():
        return Email(message='My custom email error message')


    class UserForm(ModelForm):
        class Meta:
            model = User
            email_validator = email


You can also override validators that take multiple arguments this way:

::


    def length(min=None, max=None):
        return Length(min=min, max=max, message='Wrong length')


    class UserForm(ModelForm):
        class Meta:
            model = User
            length_validator = length


Here is the full list of configuration options you can use to override default validators:

* email_validator

* length_validator

* unique_validator

* number_range_validator

* date_range_validator

* time_range_validator

* optional_validator


Disabling validators
--------------------

You can disable certain validators by assigning them as `None`. Let's say you want to disable nullable columns having `Optional` validator. This can be achieved as follows::


    class UserForm(ModelForm):
        class Meta:
            model = User
            optional_validator = None
