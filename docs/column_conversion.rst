Column to form field conversion
===============================

Basic type conversion
---------------------

By default WTForms-Alchemy converts SQLAlchemy model columns using the following
type table. So for example if an Unicode column would be converted to TextField.

The reason why so many types here convert to wtforms_components based fields is that
wtforms_components provides better HTML5 compatible type handling than WTForms at the moment.


====================================    =================
 **SQAlchemy column type**              **Form field**
------------------------------------    -----------------
    BigInteger                          wtforms_components.fields.IntegerField
    Boolean                             BooleanField
    Date                                wtforms_components.fields.DateField
    DateTime                            wtforms_components.fields.DateTimeField
    Enum                                wtforms_components.fields.SelectField
    Float                               FloatField
    Integer                             wtforms_components.fields.IntegerField
    Numeric                             wtforms_components.fields.DecimalField
    SmallInteger                        wtforms_components.fields.IntegerField
    String                              TextField
    Text                                TextAreaField
    Time                                wtforms_components.fields.TimeField
    Unicode                             TextField
    UnicodeText                         TextAreaField
====================================    =================


WTForms-Alchemy also supports many types provided by SQLAlchemy-Utils.


====================================    =================
 **SQAlchemy-Utils type**               **Form field**
------------------------------------    -----------------
    ArrowType                           wtforms_components.fields.DateTimeField
    ChoiceType                          wtforms_components.fields.SelectField
    ColorType                           wtforms_components.fields.ColorField
    CountryType                         wtforms_alchemy.fields.CountryType
    EmailType                           wtforms_components.fields.EmailField
    IPAddressType                       wtforms_components.fields.IPAddressField
    PasswordType                        wtforms.fields.PasswordField
    PhoneNumberType                     wtforms_components.fields.PhoneNumberField
    URLType                             wtforms_components.fields.StringField + URL validator
    UUIDType                            wtforms.fields.TextField + UUID validator
    WeekDaysType                        wtforms_components.fields.WeekDaysField
====================================    =================


====================================    =================
 **SQAlchemy-Utils range type**         **Form field**
------------------------------------    -----------------
    DateRangeType                       wtforms_components.fields.DateIntervalField
    DateTimeRangeType                   wtforms_components.fields.DateTimeIntervalField
    IntRangeType                        wtforms_components.fields.IntIntervalField
    NumericRangeType                    wtforms_components.fields.DecimalIntervalField
====================================    =================




Excluded fields
---------------
By default WTForms-Alchemy excludes a column from the ModelForm if one of the following conditions is True:
    * Column is primary key
    * Column is foreign key
    * Column is DateTime field which has default value (usually this is a generated value)
    * Column is of TSVectorType type
    * Column is set as model inheritance discriminator field


Using include, exclude and only
-------------------------------

If you wish the include some of the excluded fields described in the earlier chapter you can use the 'include' configuration parameter.


In the following example we include the field 'author_id' in the ArticleForm (by default it is excluded since it is a foreign key column).

::


    class Article(Base):
        __tablename__ = 'article'

        id = sa.Column(sa.Integer, primary_key=True, nullable=False)
        name = sa.Column(
            sa.Unicode(255),
            nullable=False
        )
        author_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
        author = sa.orm.relationship(User)


    class ArticleForm(Form):
        class Meta:
            include = ['author_id']


If you wish the exclude fields you can either use 'exclude' or 'only' configuration parameters. The recommended way is using only, since in most cases it is desirable to explicitly tell which fields the form should contain.

Consider the following model:

::


    class Article(Base):
        __tablename__ = 'article'

        id = sa.Column(sa.Integer, primary_key=True, nullable=False)
        name = sa.Column(
            sa.Unicode(255),
            nullable=False
        )
        content = sa.Column(
            sa.UnicodeText
        )
        description = sa.Column(
            sa.UnicodeText
        )


Now let's say we want to exclude 'description' from the form. This can be achieved as follows:

::


    class ArticleForm(Form):
        class Meta:
            exclude = ['description']


Or as follows (the recommended way):


::


    class ArticleForm(Form):
        class Meta:
            only = ['name', 'content']




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


Type decorators
---------------

WTForms-Alchemy supports SQLAlchemy TypeDecorator based types. When WTForms-Alchemy encounters a TypeDecorator typed column it tries to convert it to underlying type field.

Example::


    import sqlalchemy as sa
    from wtforms.fields import TextField, IntegerField
    from wtforms.validators import Email


    class CustomUnicodeType(sa.types.TypeDecorator):
        impl = sa.types.Unicode

    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        name = sa.Column(CustomUnicodeType(100), primary_key=True)


    class UserForm(ModelForm):
        class Meta:
            model = User


Now the name field of UserForm would be a simple TextField since the underlying type implementation is Unicode.
