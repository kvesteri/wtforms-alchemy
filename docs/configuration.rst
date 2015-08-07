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

.. warning::

    Using ``exclude`` might lead to problems in situations where you add columns to your model
    and forget to exclude those from the form by using ``exclude``, hence it is recommended to
    use ``only`` rather than ``exclude``.


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


**only**

Generates a form using only the field names provided in ``only``.

::

    class UserForm(ModelForm):
        class Meta:
            model = User
            only = ['email']


**field_args** (default: {})

This parameter can be used for overriding field arguments. In the following example we force the email field optional.

::


     class UserForm(ModelForm):
        class Meta:
            model = User
            field_args = {'email': {'validators': [Optional()]}}


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

    from wtforms.validators import Email


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

**strip_string_fields** (default: False)

Whether or not to add stripping filter to all string fields.

Example ::


    from werkzeug.datastructures import MultiDict


    class UserForm(ModelForm):
        class Meta:
            model = User
            strip_string_fields = True


    form = UserForm(MultiDict([('name', 'someone     ')]))

    assert form.name.data == 'someone'


You can also fine-grain field stripping by using trim argument for columns. In the example
below the field 'name' would have its values stripped whereas field 'password' would not. ::


    from wtforms.validators import Email


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(100))
        password = sa.Column(sa.Unicode(100), info={'trim': False})


    class UserForm(ModelForm):
        class Meta:
            model = User
            strip_string_fields = True


**form_generator** (default: FormGenerator class)

Change this if you want to use custom form generator class.


Form inheritance
----------------

ModelForm's configuration support inheritance. This means that child classes inherit
parents Meta properties.

Example::

    from wtforms.validators import Email


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


Not nullable column validation
------------------------------

WTForms-Alchemy offers two options for configuring how not nullable columns are validated:

* not_null_validator

    The default validator to be used for not nullable columns. Set this to `None`
    if you wish to disable it. By default this is `[InputRequired()]`.


* not_null_validator_type_map

    Type map which overrides the **not_null_validator** on specific column type. By default this is `ClassMap({sa.String: [InputRequired(), DataRequired()]})`.


In the following example we set `DataRequired` validator for all not nullable Enum typed columns:


::

    import sqlalchemy as sa
    from wtforms.validators import DataRequired
    from wtforms_alchemy import ClassMap


    class MyForm(ModelForm):
        class Meta:
            not_null_validator_type_map = ClassMap({sa.Enum: [DataRequired()]})



Customizing type conversion
---------------------------

You can customize the SQLAlchemy type conversion on class level with type_map Meta property.

Type map accepts dictionary of SQLAlchemy types as keys and WTForms field classes
as values. The key value pairs of this dictionary override the key value pairs of FormGenerator.TYPE_MAP.

Let's say we want to convert all unicode typed properties to TextAreaFields instead of StringFields. We can do this by assigning Unicode, TextAreaField key value pair into type map.

::


    from wtforms.fields import TextAreaField
    from wtforms_alchemy import ClassMap


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(100))


    class UserForm(ModelForm):
        class Meta:
            type_map = ClassMap({sa.Unicode: TextAreaField})


In case the type_map dictionary values are not inherited from WTForm field class, they are considered callable functions. These functions will be called with the corresponding column as their only parameter.


.. _custom_base:

Custom form base class
----------------------

You can use custom base class for your model forms by using model_form_factory
function. In the following example we have a UserForm which uses Flask-WTF
form as a parent form for ModelForm. ::


    from flask.ext.wtf import Form
    from wtforms_alchemy import model_form_factory


    ModelForm = model_form_factory(Form)


    class UserForm(ModelForm):
        class Meta:
            model = User


You can also pass any form generator option to model_form_factory. ::


    ModelForm = model_form_factory(Form, strip_string_fields=True)


    class UserForm(ModelForm):
        class Meta:
            model = User
