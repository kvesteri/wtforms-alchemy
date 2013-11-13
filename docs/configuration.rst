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


**field_args** (default: {})

This parameter can be used for overriding field arguments. In the following example we force the email field optional.

::


     class UserForm(ModelForm):
        class Meta:
            model = User
            field_args = {'email': {'validators': Optional()}}


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


You can also pass any form genrerator option to model_form_factory. ::


    ModelForm = model_form_factory(Form, strip_string_fields=True)


    class UserForm(ModelForm):
        class Meta:
            model = User
