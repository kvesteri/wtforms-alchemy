import sqlalchemy as sa
from pytest import raises

from tests import FormRelationsTestCase, MultiDict
from wtforms_alchemy import ModelForm, ModelFormField


class TestOneToOneModelFormRelations(FormRelationsTestCase):
    def create_models(self):
        class Location(self.base):
            __tablename__ = "location"
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=True)

        class Event(self.base):
            __tablename__ = "event"
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

    def save(self, event=None, data={}):
        if not data:
            data = {
                "name": "Some event",
                "location-name": "Some location",
            }
        if not event:
            event = self.Event()
        self.session.add(event)
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()
        return event

    def test_assigment_and_deletion(self):
        self.save()
        event = self.session.query(self.Event).first()
        assert event.location.name == "Some location"
        data = {"name": "Some event"}
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()
        event = self.session.query(self.Event).first()
        assert not event.location.name

    def test_only_populates_related_if_they_are_obj_attributes(self):
        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            unknown_field = ModelFormField(self.LocationForm)

        self.EventForm = EventForm

        with raises(TypeError):
            self.save(
                data={
                    "name": "Some event",
                    "unknown_field-name": "Some location",
                }
            )

    def test_updating_related_object(self):
        event = self.save()
        location_id = event.location.id
        self.save(event, {"name": "some name", "location-name": "Some other location"})
        assert event.name == "some name"
        assert event.location.id == location_id
