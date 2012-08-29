WTForms-Alchemy
===============

WTForms-Alchemy is a WTForms extension toolkit for easier creation of model
based forms.

QuickStart
----------

Lets say we have a model called User with couple of fields
::
    import sqlalchemy as sa
    from wtforms import Form
    from wtforms_alchemy import ModelForm

    class User(Entity):
        __tablename__ = 'user'

        id = sa.Column(
            sa.BigInteger, sa.ForeignKey(Entity.id), primary_key=True
        )
        name = sa.Column(sa.Unicode(100), nullable=False)
        email = sa.Column(sa.Unicode(255), nullable=False)


Now the following forms are essentially the same
::
    class UserForm(ModelForm):
        class Meta:
            model = User


    class User(Form):
        name = TextField(validators=[Required(), Length(max=100)])
        email = TextField(validators=[Required(), Length(max=255)])


API reference
-------------

.. module:: wtforms_alchemy

This part of the documentation covers all the public classes and functions
in WTForms-Alchemy.

.. autoclass:: ModelForm
