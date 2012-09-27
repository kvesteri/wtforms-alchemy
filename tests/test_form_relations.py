from pytest import raises

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from wtforms_alchemy import ModelForm
from wtforms.fields import FormField, FieldList


class MultiDict(dict):
    def getlist(self, key):
        return [self[key]]


class FormRelationsTestCase(object):
    def setup_method(self, method):
        self.engine = create_engine('sqlite:///:memory:')

        self.base = declarative_base()
        self.create_models()
        self.create_forms()

        self.base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.base.metadata.drop_all(self.engine)
        self.engine.dispose()


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

            location = FormField(LocationForm)

        self.LocationForm = LocationForm
        self.EventForm = EventForm

    def save(self, data={}):
        if not data:
            data = {
                'name': u'Some event',
                'location-name': u'Some location',
            }
        event = self.Event()
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.add(event)
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

            unknown_field = FormField(self.LocationForm)

        self.EventForm = EventForm
        self.save({
            'name': u'Some event',
            'unknown_field-name': u'Some location',
        })


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

            locations = FieldList(FormField(LocationForm))

        self.LocationForm = LocationForm
        self.EventForm = EventForm

    def save(self, data={}):
        if not data:
            data = {
                'name': u'Some event',
                'locations-0-name': u'Some location',
            }
        event = self.Event()
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.add(event)
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

            unknown_field = FieldList(FormField(self.LocationForm))

        self.EventForm = EventForm

        with raises(TypeError):
            self.save({
                'name': u'Some event',
                'unknown_field-0-name': u'Some location',
            })


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

            address = FormField(AddressForm)

        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            locations = FieldList(FormField(LocationForm))

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
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.add(event)
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

            addresses = FieldList(FormField(AddressForm))

        class EventForm(ModelForm):
            class Meta:
                model = self.Event

            location = FormField(LocationForm)

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
        form = self.EventForm(MultiDict(data))
        form.validate()
        form.populate_obj(event)
        self.session.add(event)
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
