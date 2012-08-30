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

    class User(Entity):
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


SQLAlchemy column to WTForms field conversion
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
    Numeric                 DecimalField
    Unicode                 TextField
    UnicodeText             TextAreaField
========================    =================

Configuration
-------------

The following configuration options are available for ModelForm's Meta subclass.


API reference
-------------

.. module:: wtforms_alchemy

This part of the documentation covers all the public classes and functions
in WTForms-Alchemy.

.. autoclass:: ModelForm
