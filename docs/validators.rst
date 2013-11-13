Validators
==========


Auto-assigned validators
------------------------

By default WTForms-Alchemy ModelForm assigns the following validators:
    * DataRequired validator if your column is not nullable and has no default value
    * NumberRange validator if column if of type Integer, Float or Decimal and column info parameter has min or max arguments defined
    * DateRange validator if column is of type Date or DateTime and column info parameter has min or max arguments defined
    * TimeRange validator if column is of type Time and info parameter has min or max arguments defined
    * Unique validator if column has a unique index
    * Length validator for String/Unicode columns with max length


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
