import sqlalchemy as sa
from wtforms.fields import FormField

from tests import FormRelationsTestCase, MultiDict
from wtforms_alchemy import ModelFieldList, ModelForm, ModelFormField


class TestDeepFormRelationsOneToManyToOne(FormRelationsTestCase):
    def create_models(self):
        class Event(self.base):
            __tablename__ = 'event'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)

        class Address(self.base):
            __tablename__ = 'address'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            street = sa.Column(sa.Unicode(255), nullable=True)

        class Location(self.base):
            __tablename__ = 'location'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=True)

            address_id = sa.Column(sa.Integer, sa.ForeignKey(Address.id))
            address = sa.orm.relationship(Address)

            event_id = sa.Column(sa.Integer, sa.ForeignKey(Event.id))
            event = sa.orm.relationship(Event, backref='locations')

        self.Event = Event
        self.Location = Location
        self.Address = Address

    def create_forms(self):
        class AddressForm(ModelForm):
            class Meta:
                model = self.Address

        class LocationForm(ModelForm):
            class Meta:
                model = self.Location

            address = ModelFormField(AddressForm)

        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            locations = ModelFieldList(FormField(LocationForm))

        self.LocationForm = LocationForm
        self.EventForm = EventForm
        self.AddressForm = AddressForm

    def save(self):
        data = {
            'name': u'Some event',
            'locations-0-name': u'Some location',
            'locations-0-address-street': u'Some address'
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
        assert event.locations[0].address.street == u'Some address'
        data = {
            'name': u'Some event'
        }
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()
        event = self.session.query(self.Event).first()
        assert event.locations == []


class TestDeepFormRelationsOneToOneToMany(FormRelationsTestCase):
    def create_models(self):
        class Location(self.base):
            __tablename__ = 'location'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=True)

        class Address(self.base):
            __tablename__ = 'address'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            street = sa.Column(sa.Unicode(255), nullable=True)

            location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
            location = sa.orm.relationship(Location, backref='addresses')

        class Event(self.base):
            __tablename__ = 'event'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)
            location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
            location = sa.orm.relationship(Location)

        self.Event = Event
        self.Location = Location
        self.Address = Address

    def create_forms(self):
        class AddressForm(ModelForm):
            class Meta:
                model = self.Address

        class LocationForm(ModelForm):
            class Meta:
                model = self.Location

            addresses = ModelFieldList(FormField(AddressForm))

        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            location = ModelFormField(LocationForm)

        self.LocationForm = LocationForm
        self.EventForm = EventForm
        self.AddressForm = AddressForm

    def save(self):
        data = {
            'name': u'Some event',
            'location-name': u'Some location',
            'location-addresses-0-street': u'Some address'
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
        assert event.location.addresses[0].street == u'Some address'
        data = {
            'name': u'Some event'
        }
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.commit()
        event = self.session.query(self.Event).first()
        assert event.location.addresses == []
