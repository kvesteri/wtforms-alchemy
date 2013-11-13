Form customization
==================


Custom fields
-------------

If you want to use a custom field class, you can pass it by using
form_field_class parameter for the column info dictionary.

Example ::


    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(sa.Unicode(100), primary_key=True, nullable=False)
        color = sa.Column(
            sa.String(7),
            info={'form_field_class': ColorField},
            nullable=False
        )

    class UserForm(ModelForm):
        class Meta:
            model = User

Now the 'color' field of UserForm would be a custom ColorField.


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


Custom widgets
--------------

Example::

    from wtforms import widgets


    class User(Base):
        __tablename__ = 'user'

        name = sa.Column(
            sa.Unicode(100), primary_key=True, nullable=False,
            info={'widget': widgets.HiddenInput()}
        )

    class UserForm(ModelForm):
        class Meta:
            model = User

Now the 'name' field of UserForm would use HiddenInput widget instead of TextInput.


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
