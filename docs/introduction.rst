Introduction
============

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
* By default uses wtforms_components SelectField for fields with choices. This field understands None values and renders nested datastructures as optgroups.
* Provides better Unique validator
* Supports custom user defined types as well as type decorators
* Supports SQLAlchemy-Utils datatypes
* Supports ModelForm model relations population
* Smarter field exclusion
* Smarter field conversion
* Understands join table inheritance
* Better configuration


Installation
------------

::


    pip install WTForms-Alchemy



The supported Python versions are 3.9–3.13.



QuickStart
----------

Lets say we have a model called User with couple of fields::

    import sqlalchemy as sa
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
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

    class UserForm(Form):
        name = TextField(validators=[DataRequired(), Length(max=100)])
        email = TextField(validators=[DataRequired(), Length(max=255)])

In the following chapters you'll learn how WTForms-Alchemy converts SQLAlchemy model
columns to form fields.
