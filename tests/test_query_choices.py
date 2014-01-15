from copy import copy
from itertools import chain
import operator
import six
import sqlalchemy as sa
from wtforms import Form
from wtforms_alchemy.fields import (
    ComboChoices, QueryChoices, Choices, SelectField
)
from tests import FormRelationsTestCase


class MultiDict(dict):
    def getlist(self, key):
        return [self[key]]


class TestQueryChoices(FormRelationsTestCase):
    def create_models(self):
        class User(self.base):
            __tablename__ = 'user'

            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))

        class Article(self.base):
            __tablename__ = 'article'

            id = sa.Column(sa.Integer, primary_key=True)
            author_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
            author = sa.orm.relationship(User)

        self.User = User
        self.Article = Article

    def create_forms(self):
        pass

    def test_list_of_choices(self):
        class ArticleForm(Form):
            author = SelectField(
                'Author',
                choices=['1', '2', '3']
            )

        form = ArticleForm(MultiDict({'author': '1'}))
        assert form.validate(), form.errors
        assert form.author.data == u'1'

    def test_query_choices(self):
        class ArticleForm(Form):
            author = SelectField(
                'Author',
                choices=QueryChoices(lambda: self.session.query(self.User))
            )

        self.session.add(self.User(name=u'John'))
        self.session.add(self.User(name=u'Michael'))
        self.session.commit()

        form = ArticleForm(MultiDict({'author': '1'}))
        assert form.validate(), form.errors
        assert form.author.data.name == u'John'

    def test_invalid_query_choice(self):
        class ArticleForm(Form):
            author = SelectField(
                'Author',
                choices=QueryChoices(lambda: self.session.query(self.User))
            )

        form = ArticleForm(MultiDict({'author': '1'}))
        assert not form.validate()
        assert form.errors['author'] == ['Not a valid choice']

    def test_none_choice(self):
        choices = Choices([('__None', 'No author', None)])
        assert choices['__None'] is None

    def test_combo_choices(self):
        choices = (
            Choices([('__None', 'No author', None)]) +
            QueryChoices(lambda: self.session.query(self.User))
        )
        self.session.add(self.User(name=u'John'))
        self.session.add(self.User(name=u'Michael'))
        self.session.commit()

        assert choices['__None'] is None

    def test_select_field_iter_choices(self):
        class ArticleForm(Form):
            author = SelectField(
                'Author',
                choices=(
                    Choices([('__None', 'No author', None)]) +
                    QueryChoices(lambda: self.session.query(self.User))
                )
            )

        self.session.add(self.User(name=u'John'))
        self.session.add(self.User(name=u'Michael'))
        self.session.commit()

        form = ArticleForm(MultiDict({'author': '__None'}))

        assert 'No author' in str(form.author)

    def test_query_choices_with_other_choices(self):
        class ArticleForm(Form):
            author = SelectField(
                'Author',
                choices=(
                    Choices([('__None', 'No author', None)]) +
                    QueryChoices(lambda: self.session.query(self.User))
                )
            )

        self.session.add(self.User(name=u'John'))
        self.session.add(self.User(name=u'Michael'))
        self.session.commit()

        form = ArticleForm(MultiDict({'author': '__None'}))
        assert form.validate(), form.errors
        assert form.author.data == None
