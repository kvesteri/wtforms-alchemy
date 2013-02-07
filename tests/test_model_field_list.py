from pytest import raises

import sqlalchemy as sa
from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
from tests import FormRelationsTestCase, MultiDict


class TestOneToManyModelFormRelations(FormRelationsTestCase):
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

    def create_forms(self):
        class LocationForm(ModelForm):
            class Meta:
                model = self.Location

        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            locations = ModelFieldList(FormField(LocationForm))

        self.LocationForm = LocationForm
        self.EventForm = EventForm

    def save(self, data={}):
        if not data:
            data = {
                'name': u'Some event',
                'locations-0-name': u'Some location',
            }
        event = self.Event()
        self.session.add(event)
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()

    def test_assigment_and_deletion(self):
        self.save()
        event = self.session.query(self.Event).first()
        assert event.locations[0].name == u'Some location'
        data = {
            'name': u'Some event'
        }
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()
        event = self.session.query(self.Event).first()
        assert event.locations == []

    def test_only_populates_related_if_they_are_obj_attributes(self):
        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            unknown_field = ModelFieldList(FormField(self.LocationForm))

        self.EventForm = EventForm

        with raises(TypeError):
            self.save({
                'name': u'Some event',
                'unknown_field-0-name': u'Some location',
            })

    def test_only_deletes_persistent_objects(self):
        data = {
            'name': u'Some event',
            'location-0-name': u'Some location',
        }

        event = self.Event(locations=[self.Location()])
        self.session.add(event)
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()
