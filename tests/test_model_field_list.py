import sqlalchemy as sa
from wtforms.fields import FormField
from wtforms_components import PassiveHiddenField

from tests import FormRelationsTestCase, MultiDict
from wtforms_alchemy import ModelFieldList, ModelForm


class ModelFieldListTestCase(FormRelationsTestCase):
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

    def save(self, event=None, data=None):
        if not data:
            data = {
                'name': u'Some event',
                'locations-0-name': u'Some location',
                'locations-0-description': u'Some description'
            }
        if not event:
            event = self.Event()
            self.session.add(event)
            form = self.EventForm(MultiDict(data))
        else:
            form = self.EventForm(MultiDict(data), obj=event)

        form.validate()
        form.populate_obj(event)
        self.session.commit()
        return event


class TestReplaceStrategy(ModelFieldListTestCase):
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


class TestUpdateStrategy(ModelFieldListTestCase):
    def create_models(self):
        class Event(self.base):
            __tablename__ = 'event'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)

        class Location(self.base):
            __tablename__ = 'location'
            TYPES = (u'', u'football field', u'restaurant')

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=True)
            description = sa.Column(sa.Unicode(255), default=u'')
            type = sa.Column(
                sa.Unicode(255),
                info={'choices': zip(TYPES, TYPES)},
                default=u''
            )

            event_id = sa.Column(sa.Integer, sa.ForeignKey(Event.id))
            event = sa.orm.relationship(Event, backref='locations')

            def __repr__(self):
                return 'Location(id=%r, name=%r)' % (self.id, self.name)

        self.Event = Event
        self.Location = Location

    def create_forms(self):
        class LocationForm(ModelForm):
            class Meta:
                model = self.Location
                only = ['name', 'description', 'type']

            id = PassiveHiddenField()

        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            locations = ModelFieldList(
                FormField(LocationForm),
                population_strategy='update'
            )

        self.LocationForm = LocationForm
        self.EventForm = EventForm

    def test_with_none_as_formdata_for_existing_objects(self):
        event = self.save()
        form = self.EventForm(MultiDict(), obj=event)
        assert form.locations[0].data['id']

    def test_single_entry_update(self):
        event = self.save()
        location_id = event.locations[0].id
        data = {
            'name': u'Some event',
            'locations-0-id': location_id,
            'locations-0-name': u'Some other location'
        }
        self.save(event, data)

        assert len(event.locations) == 1
        assert event.locations[0].id == location_id
        assert event.locations[0].name == u'Some other location'

    def test_creates_new_objects_for_entries_with_unknown_identifiers(self):
        event = self.save()
        location_id = event.locations[0].id
        data = {
            'name': u'Some event',
            'locations-0-id': 12,
            'locations-0-name': u'Some other location'
        }
        self.save(event, data)
        assert event.locations
        assert event.locations[0].id != location_id

    def test_replace_entry(self):
        data = {
            'name': u'Some event',
            'locations-0-name': u'Some location',
            'locations-0-description': u'Some description',
            'locations-0-type': u'restaurant'
        }
        event = self.save(data=data)
        location_id = event.locations[0].id
        self.session.commit()
        data = {
            'name': u'Some event',
            'locations-0-name': u'Some other location',
        }
        self.save(event, data)
        location = event.locations[0]
        assert location.id != location_id
        assert location.name == u'Some other location'
        assert location.description == u''
        assert location.type == u''
        assert len(event.locations) == 1

    def test_replace_and_update(self):
        data = {
            'name': u'Some event',
            'locations-0-name': u'Location 1',
            'locations-0-description': u'Location 1 description',
            'locations-1-name': u'Location 2',
            'locations-1-description': u'Location 2 description',
        }
        event = self.save(data=data)
        self.session.commit()
        data = {
            'name': u'Some event',
            'locations-0-id': event.locations[1].id,
            'locations-0-name': u'Location 2 updated',
            'locations-0-description': u'Location 2 description updated',
            'locations-1-name': u'Location 3',
        }
        self.save(event, data)
        self.session.commit()
        location = event.locations[0]
        location2 = event.locations[1]
        assert location.name == u'Location 2 updated'
        assert location.description == u'Location 2 description updated'
        assert len(event.locations) == 2
        assert location2.name == u'Location 3'
        assert location2.description == u''

    def test_multiple_entries(self):
        event = self.save()
        location_id = event.locations[0].id
        data = {
            'name': u'Some event',
            'locations-0-name': u'Some location',
            'locations-1-id': str(location_id),  # test coercing works
            'locations-1-name': u'Some other location',
            'locations-2-name': u'Third location',
            'locations-3-id': 123,
            'locations-3-name': u'Fourth location'
        }
        self.save(event, data)
        assert len(event.locations) == 4
        assert event.locations[0].id == location_id
        assert event.locations[0].name == u'Some other location'
        assert event.locations[1].name == u'Some location'
        assert event.locations[2].name == u'Third location'
        assert event.locations[3].name == u'Fourth location'

    def test_delete_all_field_list_entries(self):
        event = self.save()
        data = {
            'name': u'Some event'
        }
        self.save(event, data)
        assert not event.locations

    def test_update_and_remove(self):
        location = self.Location(
            name=u'Location #2'
        )
        event = self.Event(
            name=u'Some event',
            locations=[
                self.Location(
                    name=u'Location #1'
                ),
                location
            ]
        )
        self.session.add(event)
        self.session.commit()
        data = {
            'locations-0-id': location.id,
            'locations-0-name': u'Location',
        }
        self.save(event, data)
        self.session.refresh(event)
        assert len(event.locations) == 1
        assert event.locations[0] == location
