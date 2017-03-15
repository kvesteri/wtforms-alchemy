Advanced concepts
=================

Using WTForms-Alchemy with SQLAlchemy-Defaults
----------------------------------------------

WTForms-Alchemy works wonderfully with `SQLAlchemy-Defaults`_. When using `SQLAlchemy-Defaults`_ with WTForms-Alchemy you
can define your models and model forms with much more robust syntax. For more information see `SQLAlchemy-Defaults`_ documentation.


.. _SQLAlchemy-Defaults: https://github.com/kvesteri/sqlalchemy-defaults


Example ::

    from sqlalchemy_defaults import LazyConfigured


    class User(Base, LazyConfigured):
        __tablename__ = 'user'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(
            sa.Unicode(255),
            nullable=False,
            label=u'Name'
        )
        age = sa.Column(
            sa.Integer,
            nullable=False,
            min=18,
            max=100,
            label=u'Age'
        )


    class UserForm(ModelForm):
        class Meta:
            model = User


Using WTForms-Alchemy with Flask-WTF
------------------------------------

In order to make WTForms-Alchemy work with `Flask-WTF`_ you need the following snippet:

.. _Flask-WTF: https://github.com/lepture/flask-wtf/

::


    from flask_wtf import FlaskForm
    from wtforms_alchemy import model_form_factory
    # The variable db here is a SQLAlchemy object instance from
    # Flask-SQLAlchemy package
    from myproject.extensions import db

    BaseModelForm = model_form_factory(FlaskForm)

    class ModelForm(BaseModelForm):
        @classmethod
        def get_session(self):
            return db.session

Then you can use the ModelForm just like before:


::


    class UserForm(ModelForm):
        class Meta:
            model = User
