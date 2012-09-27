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

QuickStart
----------

Lets say we have a model called User with couple of fields::

    import sqlalchemy as sa
    from wtforms import Form
    from wtforms_alchemy import ModelForm

    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.BigInteger, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode(100), nullable=False)
        email = sa.Column(sa.Unicode(255), nullable=False)


Now the following forms are essentially the same::

    class UserForm(ModelForm):
        class Meta:
            model = User


    class User(Form):
        name = TextField(validators=[Required(), Length(max=100)])
        email = TextField(validators=[Required(), Length(max=255)])


Field type conversion
---------------------------------------------
========================    =================
 SQAlchemy column type      WTForms Field
------------------------    -----------------
    BigInteger              IntegerField
    Date                    DateField
    DateTime                DateTimeField
    Enum                    SelectField
    Float                   FloatField
    Integer                 IntegerField
    Integer                 IntegerField
    Numeric                 DecimalField
    SmallInteger            IntegerField
    Text                    TextAreaField
    Unicode                 TextField
    UnicodeText             TextAreaField
========================    =================

Using choices parameter
-----------------------

Sometimes you may want to have integer and unicode fields convert to SelectFields.
Probably the easiest way to achieve this is by using choices parameter for the column
info dictionary.

Example ::


    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        age = sa.Column(
            sa.Integer,
            info={'choices': [i for i in xrange(13, 99)]},
            nullable=False
        )

    class UserForm(ModelForm):
        class Meta:
            model = User


Here the UserForm would have two fields. One TextField for the name column and one
SelectField for the age column containing range of choices from 13 to 99.

Configuration
-------------

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


Adding column descriptions
--------------------------

Example::

    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        email = sa.Column(
            sa.Unicode(255),
            nullable=False,
            info={'description': 'This is the description of email.'}
        )



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
use model User and have additional Email validator on column 'email'.


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
--------------------

WTForms-Alchemy undestands Form relations and is smart enough to populate related
objects accordingly. Consider the following example. We have Event and Location
classes with each event having one location. ::

    from sqlalchemy.ext.declarative import declarative_base
    from wtforms_alchemy import ModelForm

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

        location = FormField(LocationForm)

Now if we populate the EventForm, WTForms-Alchemy is smart enough to populate related
location too. ::

    event = Event()
    form = EventForm(request.POST)
    form.populate_obj(event)


API reference
-------------

.. module:: wtforms_alchemy

This part of the documentation covers all the public classes and functions
in WTForms-Alchemy.

.. autoclass:: ModelForm
