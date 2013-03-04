WTForms-Alchemy
===============

WTForms-Alchemy is a WTForms extension toolkit for easier creation of model
based forms. Strongly influenced by Django ModelForm.

What for?
---------
Many times when building modern web apps with SQLAlchemy you’ll have forms that
map closely to models. For example, you might have a Article model,
and you want to create a form that lets people post new article. In this case,
it would be time-consuming to define the field types and basic validators in
your form, because you’ve already defined the fields in your model.

WTForms-Alchemy provides a helper class that let you create a Form class from a
SQLAlchemy model.

Differences with wtforms.ext.sqlalchemy model_form
--------------------------------------------------

WTForms-Alchemy does not try to replace all the functionality of wtforms.ext.sqlalchemy.
It only tries to replace the model_form function of wtforms.ext.sqlalchemy by a much better solution.
Other functionality of .ext.sqlalchemy such as QuerySelectField and QuerySelectMultipleField can be used
along with WTForms-Alchemy.

Now how is WTForms-Alchemy ModelForm better than wtforms.ext.sqlachemy's model_form?

* Provides explicit declaration of ModelForms (much easier to override certain columns)
* Form generation supports Unique and NumberRange validators
* Form inheritance support (along with form configuration inheritance)
* Automatic SelectField type coercing based on underlying column type
* Provides special SelectField that understands None values. This SelectField also renders nested datastructures as optgroups
* Provides better Unique validator
* Supports ModelForm model relations population
* Smarter field exclusion
* Smarter field conversion
* Understands join table inheritance
* Better configuration


QuickStart
----------

Lets say we have a model called User with couple of fields::

    import sqlalchemy as sa
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from wtforms_alchemy import ModelForm

    engine = create_engine('sqlite:///:memory:')
    Base = declarative_base(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.BigInteger, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode(100), nullable=False)
        email = sa.Column(sa.Unicode(255), nullable=False)


Now we can create our first ModelForm for the User model. ModelForm behaves almost
like your ordinary WTForms Form except it accepts special Meta arguments. Every ModelForm
must define model parameter in the Meta arguments.::

    class UserForm(ModelForm):
        class Meta:
            model = User


Now this ModelForm is essentially the same as ::

    class User(Form):
        name = TextField(validators=[DataRequired(), Length(max=100)])
        email = TextField(validators=[DataRequired(), Length(max=255)])

In the following chapters you'll learn how WTForms-Alchemy converts SQLAlchemy model
columns to form fields.


Custom fields and validators
============================

While the main purpose of WTForms-Alchemy is to provide a bridge between SQLAlchemy
models and WTForms forms. It also provides some additional fields and validators missing
from WTForms.

SelectField
-----------

This SelectField provides support for optgroups.


DateRange validator
-------------------

The DateRange validator is essentially the same as wtforms.validators.NumberRange validator but validates
dates.

In the following example we define a start_time field, which does not accept dates in the past. ::

    from datetime import datetime
    from wtforms import Form
    from wtforms.fields import DateField
    from wtforms_alchemy import DateRange

    class EventForm(Form):
        start_time = DateField(
            validators=[DateRange(min=datetime.now())]
        )

If validator
------------

The If validator provides means for having conditional validations. In the following example we only
validate field email if field user_id is provided. ::


    from wtforms import Form
    from wtforms.fields import IntegerField, TextField
    from wtforms_alchemy import If

    class SomeForm(Form):
        user_id = IntegerField()
        email = TextField(validators=[
            If(lambda form, field: field.user_id.data, Email())
        ])


Chain validator
---------------


Chain validator chains validators together. Chain validator can be combined with If validator
to provide nested conditional validations. ::


    from wtforms import Form
    from wtforms.fields import IntegerField, TextField
    from wtforms_alchemy import If

    class SomeForm(Form):
        user_id = IntegerField()
        email = TextField(validators=[
            If(
                lambda form, field: field.user_id.data,
                Chain(DataRequired(), Email())
            )
        ])


Converting model columns to form fields
=======================================

Basic type conversion
---------------------

By default WTForms-Alchemy converts SQLAlchemy model columns using the following
type table. So for example if an Unicode column would be converted to TextField.


========================    =================
 SQAlchemy column type      WTForms Field
------------------------    -----------------
    BigInteger              IntegerField
    Date                    DateField
    DateTime                DateTimeField
    Enum                    wtforms_alchemy.fields.SelectField
    Float                   FloatField
    Integer                 IntegerField
    Integer                 IntegerField
    Numeric                 DecimalField
    SmallInteger            IntegerField
    Text                    TextAreaField
    Unicode                 TextField
    UnicodeText             TextAreaField
========================    =================

Excluded fields
---------------
By default WTForms-Alchemy excludes a column from the ModelForm if one of the following conditions is True:
    * Column is primary key
    * Column is foreign key
    * Column is DateTime field which has default value (usually this is a generated value)
    * Column is set as model inheritance discriminator field

Forcing the use of SelectField
------------------------------

Sometimes you may want to have integer and unicode fields convert to SelectFields.
Probably the easiest way to achieve this is by using choices parameter for the column
info dictionary.

Example ::


    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        age = sa.Column(
            sa.Integer,
            info={'choices': [(i, i) for i in xrange(13, 99)]},
            nullable=False
        )

    class UserForm(ModelForm):
        class Meta:
            model = User


Here the UserForm would have two fields. One TextField for the name column and one
SelectField for the age column containing range of choices from 13 to 99.

Notice that WTForms-Alchemy is smart enough to use the right coerce function based on
the underlying column type, hence in the previous example the age column would convert
to the following SelectField. ::


    SelectField('Age', coerce=int, choices=[(i, i) for i in xrange(13, 99)])


For nullable unicode and string columns WTForms-Alchemy uses special null_or_unicode
coerce function, which converts empty strings to None values.


Field descriptions
------------------

Example::

    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        email = sa.Column(
            sa.Unicode(255),
            nullable=False,
            info={'description': 'This is the description of email.'}
        )

    class UserForm(ModelForm):
        class Meta:
            model = User

Now the 'email' field of UserForm would have description 'This is the description of email.'


Field labels
------------

Example::

    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(
            sa.Unicode(100), primary_key=True, nullable=False,
            info={'label': 'Name'}
        )

    class UserForm(ModelForm):
        class Meta:
            model = User

Now the 'name' field of UserForm would have label 'Name'.


Default values
--------------

By default WTForms-Alchemy ModelForm assigns the default values from column definitions.
Example ::

    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        level = sa.Column(sa.Integer, default=1)

    class UserForm(ModelForm):
        class Meta:
            model = User

Now the UseForm 'level' field default value would be 1.


Auto-assigned validators
------------------------

By default WTForms-Alchemy ModelForm assigns the following validators:
    * DataRequired validator if your column is not nullable and has no default value
    * NumberRange validator if column info parameter has min or max arguments defined
    * DateRange validator if column info parameter has min or max arguments defined
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


    Unique(User.email)


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



Adding/overriding fields
------------------------

Example::

    from wtforms.fields import TextField, IntegerField
    from wtforms.validators import Email

    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        email = sa.Column(
            sa.Unicode(255),
            nullable=False
        )

    class UserForm(ModelForm):
        class Meta:
            model = User

        email = TextField(validators=[Optional()])
        age = IntegerField()

Now the UserForm would have three fields:
    * name, a required TextField
    * email, an optional TextField
    * age, IntegerField


Form inheritance
----------------

ModelForm's configuration support inheritance. This means that child classes inherit
parents Meta properties.

Example::

    from wtfroms.validators import Email


    class UserForm(ModelForm):
        class Meta:
            model = User
            validators = {'email': [Email()]}


    class UserUpdateForm(UserForm):
        class Meta:
            all_fields_optional = True


Here UserUpdateForm inherits the configuration properties of UserForm, hence it would
use model User and have additional Email validator on column 'email'. Also it assigns
all fields as optional.


Configuration
=============

ModelForm meta parameters
-------------------------

The following configuration options are available for ModelForm's Meta subclass.

**include_primary_keys** (default: False)

If you wish to include primary keys in the generated form please set this to True.
This is useful when dealing with natural primary keys. In the following example each
user has a natural primary key on its column name.

The UserForm would contain two fields name and email. ::

    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        email = sa.Column(sa.Unicode(255), nullable=False)


    class UserForm(ModelForm):
        class Meta:
            model = User
            include_primary_keys = True


**exclude**

You can exclude certain fields by adding them to the exclude list. ::

    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        email = sa.Column(sa.Unicode(255), nullable=False)


    class UserForm(ModelForm):
        class Meta:
            model = User
            include_primary_keys = True
            exclude = ['email']
            # this form contains only 'name' field


**include_foreign_keys** (default: False)

Foreign keys can be included in the form by setting include_foreign_keys to True.

**only_indexed_fields** (default: False)

When setting this option to True, only fields that have an index will be included in
the form. This is very useful when creating forms for searching a specific model.


**include_datetimes_with_default** (default: False)

When setting this option to True, datetime with default values will be included in the
form. By default this is False since usually datetime fields that have default values
are generated columns such as "created_at" or "updated_at", which should not be included
in the form.


**validators**

A dict containing additional validators for the generated form field objects.

Example::

    from wtfroms.validators import Email


    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        email = sa.Column(sa.Unicode(255), nullable=False)


    class UserForm(ModelForm):
        class Meta:
            model = User
            include_primary_keys = True
            validators = {'email': [Email()]}

**datetime_format** (default: '%Y-%m-%d %H:%M:%S')

Defines the default datetime format, which will be assigned to generated datetime
fields.

**date_format** (default: '%Y-%m-%d')

Defines the default date format, which will be assigned to generated datetime
fields.


**all_fields_optional** (default: False)

Defines all generated fields as optional (useful for update forms).

**assign_required** (default: True)

Whether or not to assign non-nullable fields as required.

**form_generator** (default: FormGenerator class)

Change this if you want to use custom form generator class.


Custom form base class
----------------------

You can use custom base class for your model forms by using model_form_factory
function. In the following example we have a UserForm which uses Flask-WTF
form as a parent form for ModelForm. ::

    from flask.ext.wtf import Form
    from wtforms_alchemy import model_form_factory


    class UserForm(model_form_factory(Form)):
        class Meta:
            model = User


Forms with relations
====================

WTForms-Alchemy provides special Field subtypes ModelFormField and ModelFieldList.
When using these types WTForms-Alchemy undestands model relations and is smart enough to populate related
objects accordingly.

One-to-one relations
--------------------

Consider the following example. We have Event and Location
classes with each event having one location. ::

    from sqlalchemy.ext.declarative import declarative_base
    from wtforms_alchemy import ModelForm, ModelFormField

    Base = declarative_base()


    class Location(Base):
        __tablename__ = 'location'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=True)

    class Event(Base):
        __tablename__ = 'event'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=False)
        location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
        location = sa.orm.relationship(Location)

    class LocationForm(ModelForm):
        class Meta:
            model = Location

    class EventForm(ModelForm):
        class Meta:
            model = Event

        location = ModelFormField(LocationForm)

Now if we populate the EventForm, WTForms-Alchemy is smart enough to populate related
location too. ::

    event = Event()
    form = EventForm(request.POST)
    form.populate_obj(event)



One-to-many relations
---------------------

Consider the following example. We have Event and Location
classes with each event having many location. Notice we are using FormField along
with ModelFieldList. ::

    from sqlalchemy.ext.declarative import declarative_base
    from wtforms_alchemy import ModelForm, ModelFieldList
    from wtforms.fields import FormField

    Base = declarative_base()


    class Event(Base):
        __tablename__ = 'event'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=False)


    class Location(Base):
        __tablename__ = 'location'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=True)

        event_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
        event = sa.orm.relationship(
            Location,
            backref='locations'  # the event needs to have this
        )


    class LocationForm(ModelForm):
        class Meta:
            model = Location


    class EventForm(ModelForm):
        class Meta:
            model = Event

        locations = ModelFieldList(FormField(LocationForm))

Now if we populate the EventForm, WTForms-Alchemy is smart enough to populate related
locations too. ::

    event = Event()
    form = EventForm(request.POST)
    form.populate_obj(event)


API Documentation
=================

This part of the documentation covers all the public classes and functions
in WTForms-Alchemy.

.. module:: wtforms_alchemy
.. autoclass:: FormGenerator
    :members:

.. include:: ../CHANGES.rst


License
=======

.. include:: ../LICENSE
