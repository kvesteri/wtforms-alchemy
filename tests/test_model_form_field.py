from flexmock import flexmock
import sqlalchemy as sa
from wtforms_alchemy import ModelForm, ModelFormField
from tests import FormRelationsTestCase, MultiDict


class TestOneToOneModelFormRelations(FormRelationsTestCase):
    def create_models(self):
        class Location(self.base):
            __tablename__ = 'location'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=True)

        class Event(self.base):
            __tablename__ = 'event'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)
            location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
            location = sa.orm.relationship(Location)

        self.Event = Event
        self.Location = Location

    def create_forms(self):
        class LocationForm(ModelForm):
            class Meta:
                model = self.Location

        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            location = ModelFormField(LocationForm)

        self.LocationForm = LocationForm
        self.EventForm = EventForm

    def save(self, data={}):
        if not data:
            data = {
                'name': u'Some event',
                'location-name': u'Some location',
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
        assert event.location.name == u'Some location'
        data = {
            'name': u'Some event'
        }
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()
        event = self.session.query(self.Event).first()
        assert event.location.name is u''

    def test_only_populates_related_if_they_are_obj_attributes(self):
        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            unknown_field = ModelFormField(self.LocationForm)

        self.EventForm = EventForm
        self.save({
            'name': u'Some event',
            'unknown_field-name': u'Some location',
        })

    def test_only_deletes_persistent_objects(self):
        data = {
            'name': u'Some event',
            'location-name': u'Some location'
        }
        flexmock(self.session).should_receive('delete').never()
        event = self.Event(location=self.Location())
        self.session.add(event)
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()
