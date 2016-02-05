import sqlalchemy as sa
from wtforms.fields import FormField
from wtforms_components import PassiveHiddenField

from tests import ModelFormTestCase, MultiDict
from wtforms_alchemy import ModelFieldList, ModelForm
from wtforms_alchemy.fields import QuerySelectField, QuerySelectMultipleField


class ModelFieldListTestCase(ModelFormTestCase):
    def create_models(self):
        class Event(self.base):
            __tablename__ = 'event'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)

        class Location(self.base):
            __tablename__ = 'location'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=True)

            event_id = sa.Column(sa.Integer, sa.ForeignKey(Event.id))
            event = sa.orm.relationship(Event, backref='locations')

        self.Event = Event
        self.Location = Location


class TestNoIncludeRelationships(ModelFieldListTestCase):
    def test_no_include_relationships_many_to_one(self):
        self.create_models()
        self.ModelTest = self.Location

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

        self.form_class = ModelTestForm

        assert not self.has_field('event')

    def test_no_include_relationships_one_to_many(self):
        self.create_models()
        self.ModelTest = self.Event

        class ModelTestForm(ModelForm):
            class Meta:
                model = self.ModelTest

        self.form_class = ModelTestForm

        assert not self.has_field('locations')


class TestIncludeRelationships(ModelFieldListTestCase):
    def test_include_relationships_many_to_one(self):
        self.create_models()
        self.ModelTest = self.Location

        class ModelTestForm(ModelForm):
            class Meta:
                include_relationships = True
                model = self.ModelTest

        self.form_class = ModelTestForm

        assert self.has_field('event')
        field = self._make_form().event
        assert isinstance(field, QuerySelectField)

    def test_include_relationships_one_to_many(self):
        self.create_models()
        self.ModelTest = self.Event

        class ModelTestForm(ModelForm):
            class Meta:
                include_relationships = True
                model = self.ModelTest

        self.form_class = ModelTestForm

        assert self.has_field('locations')
        field = self._make_form().locations
        assert isinstance(field, QuerySelectMultipleField)
