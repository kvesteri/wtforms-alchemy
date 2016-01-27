import sqlalchemy as sa
from pytest import mark, raises
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from wtforms import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import TextField

from tests import MultiDict
from wtforms_alchemy import ModelForm, Unique

base = declarative_base()


class Color(base):
    __tablename__ = 'color'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255), unique=True)


class User(base):
    __tablename__ = 'event'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255), unique=True)
    email = sa.Column(sa.Unicode(255))
    favorite_color_id = sa.Column(sa.Integer, sa.ForeignKey(Color.id))
    favorite_color = relationship(Color)


class TestUniqueValidator(object):
    def create_models(self):
        # This is a hack so we can use our classes
        # without initializing self first
        self.base = base

    def setup_method(self, method):
        self.engine = sa.create_engine('sqlite:///:memory:')

        self.base = declarative_base()
        self.create_models()

        self.base.metadata.create_all(self.engine)

        Session = sa.orm.session.sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _test_syntax(self, column, expected_dict):
        class MyForm(ModelForm):
            name = TextField()
            email = TextField()

        validator = Unique(
            column,
            get_session=lambda: self.session
        )
        form = MyForm()
        if not hasattr(form, 'Meta'):
            form.Meta = lambda: None
        form.Meta.model = User
        result = validator._syntaxes_as_tuples(form, form.name, column)
        assert result == expected_dict

    def test_with_form_obj_unavailable(self):
        class MyForm(Form):
            name = TextField(
                validators=[
                    Unique(User.name, get_session=lambda: self.session)
                ]
            )

        form = MyForm()
        with raises(Exception) as e:
            form.validate()
        assert "Couldn't access Form._obj attribute" in str(e)

    @mark.parametrize(['column', 'expected_dict'], (
        (User.name, (('name', User.name),)),
        ('name', (('name', User.name),)),
        (('name', 'email'), (('name', User.name), ('email', User.email))),
        ({'exampleName': User.name}, (('exampleName', User.name),)),
        (
            (User.name, User.email),
            (('name', User.name), ('email', User.email))
        ),
        (
            (User.name, User.favorite_color),
            (('name', User.name), ('favorite_color', User.favorite_color))
        ),
    ))
    def test_columns_as_tuples(self, column, expected_dict):
        self._test_syntax(column, expected_dict)

    def test_columns_as_tuples_classical_mapping(self):
        users = sa.Table(
            'users',
            sa.MetaData(None),
            sa.Column('name', sa.Unicode(255))
        )
        self._test_syntax(
            users.c.name,
            (('name', users.c.name),)
        )

    @mark.parametrize('column', (
        User.name,
        {'name': User.name},
        (('name', User.name),)
    ))
    def test_raises_exception_if_improperly_configured(self, column):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    column,
                )]
            )
        with raises(Exception):
            MyForm().validate()

    def test_raises_exception_string_if_improperly_configured(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    ('name', 'email'),
                )]
            )
        with raises(Exception):
            MyForm().validate()

    def test_existing_name_collision(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    User.name,
                    get_session=lambda: self.session
                )]
            )

        self.session.add(User(name=u'someone'))
        self.session.commit()

        form = MyForm(MultiDict({'name': u'someone'}))
        form.validate()
        assert form.errors == {'name': [u'Already exists.']}

    def test_existing_name_collision_multiple(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    [User.name, User.email],
                    get_session=lambda: self.session
                )]
            )
            email = TextField()

        self.session.add(User(
            name=u'someone',
            email=u'someone@example.com'
        ))
        self.session.commit()

        form = MyForm(MultiDict({
            'name': u'someone',
            'email': u'someone@example.com'
        }))
        form.validate()
        assert form.errors == {'name': [u'Already exists.']}

    def test_works_with_flask_sqlalchemy_syntax(self, monkeypatch):
        monkeypatch.setattr(User, 'query', self.session.query(User), False)

        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    [User.name, User.email],
                    get_session=lambda: self.session
                )]
            )
            email = TextField()

        self.session.add(User(
            name=u'someone',
            email=u'someone@example.com'
        ))
        self.session.commit()

        form = MyForm(MultiDict({
            'name': u'someone',
            'email': u'someone@example.com'
        }))
        form.validate()
        assert form.errors == {'name': [u'Already exists.']}

    def test_existing_name_collision_classical_mapping(self):
        sa.Table(
            'user',
            sa.MetaData(None),
            sa.Column('name', sa.String(255)),
            sa.Column('email', sa.String(255))
        )

        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    [User.name, User.email],
                    get_session=lambda: self.session
                )]
            )
            email = TextField()

        self.session.add(User(
            name=u'someone',
            email=u'someone@example.com'
        ))
        self.session.commit()

        form = MyForm(MultiDict({
            'name': u'someone',
            'email': u'someone@example.com'
        }))
        form.validate()
        assert form.errors == {'name': [u'Already exists.']}

    def test_relationship_multiple_collision(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    [User.name, User.favorite_color],
                    get_session=lambda: self.session
                )]
            )
            email = TextField()
            favorite_color = QuerySelectField(
                query_factory=lambda: self.session.query(Color).all(),
                allow_blank=True
            )

        red_color = Color(name='red')
        blue_color = Color(name='blue')
        self.session.add(red_color)
        self.session.add(blue_color)
        self.session.add(User(
            name=u'someone',
            email=u'first.email@example.com',
            favorite_color=red_color
        ))
        self.session.commit()

        form = MyForm(MultiDict({
            'name': u'someone',
            'email': u'second.email@example.com',
            'favorite_color': str(red_color.id)
        }))
        form.validate()
        assert form.errors == {'name': [u'Already exists.']}

    def test_relationship_multiple_no_collision(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    [User.name, User.favorite_color],
                    get_session=lambda: self.session
                )]
            )
            email = TextField()
            favorite_color = QuerySelectField(
                query_factory=lambda: self.session.query(Color).all(),
                allow_blank=True
            )

        red_color = Color(name='red')
        blue_color = Color(name='blue')
        self.session.add(red_color)
        self.session.add(blue_color)
        self.session.add(User(
            name=u'someone',
            email=u'first.email@example.com',
            favorite_color=red_color
        ))
        self.session.commit()

        form = MyForm(MultiDict({
            'name': u'someone',
            'email': u'second.email@example.com',
            'favorite_color': str(blue_color.id)
        }))
        form.validate()
        assert form.errors == {}

    def test_without_obj_without_collision(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    User.name,
                    get_session=lambda: self.session
                )]
            )

        self.session.add(User(name=u'someone else'))
        self.session.commit()

        form = MyForm(MultiDict({'name': u'someone'}))
        assert form.validate()

    def test_without_obj_without_collision_multiple(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    [User.name, User.email],
                    get_session=lambda: self.session
                )]
            )
            email = TextField()

        self.session.add(User(
            name=u'someone',
            email=u'someone@example.com'
        ))
        self.session.commit()

        form = MyForm(MultiDict({
            'name': u'someone',
            'email': u'else@example.com'
        }))
        assert form.validate()

    def test_existing_name_no_collision(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    User.name,
                    get_session=lambda: self.session
                )]
            )

        obj = User(name=u'someone')
        self.session.add(obj)

        form = MyForm(MultiDict({'name': u'someone'}), obj=obj)
        assert form.validate()

    def test_existing_name_no_collision_multiple(self):
        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    (User.name, User.email),
                    get_session=lambda: self.session
                )]
            )
            email = TextField()

        obj = User(name=u'someone', email=u'hello@world.com')
        self.session.add(obj)

        form = MyForm(MultiDict(
            {'name': u'someone', 'email': 'hello@world.com'}
        ), obj=obj)
        assert form.validate()

    def test_supports_model_query_parameter(self):
        User.query = self.session.query(User)

        class MyForm(ModelForm):
            name = TextField(
                validators=[Unique(
                    User.name,
                )]
            )

        form = MyForm(MultiDict({'name': u'someone'}))
        assert form.validate()
