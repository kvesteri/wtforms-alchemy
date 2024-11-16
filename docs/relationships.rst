Forms with relations
====================

WTForms-Alchemy provides special Field subtypes ModelFormField and ModelFieldList.
When using these types WTForms-Alchemy understands model relations and is smart enough to populate related
objects accordingly.

One-to-one relations
--------------------

Consider the following example. We have Event and Location
classes with each event having one location. ::

    from sqlalchemy.orm import declarative_base
    from wtforms_alchemy import ModelForm, ModelFormField

    Base = declarative_base()


    class Location(Base):
        __tablename__ = 'location'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=True)

    class Event(Base):
        __tablename__ = 'event'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=False)
        location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
        location = sa.orm.relationship(Location)

    class LocationForm(ModelForm):
        class Meta:
            model = Location

    class EventForm(ModelForm):
        class Meta:
            model = Event

        location = ModelFormField(LocationForm)

Now if we populate the EventForm, WTForms-Alchemy is smart enough to populate related
location too. ::

    event = Event()
    form = EventForm(request.POST)
    form.populate_obj(event)



One-to-many relations
---------------------

Consider the following example. We have Event and Location
classes with each event having many location. Notice we are using FormField along
with ModelFieldList. ::

    from sqlalchemy.orm import declarative_base
    from wtforms_alchemy import ModelForm, ModelFieldList
    from wtforms.fields import FormField

    Base = declarative_base()


    class Event(Base):
        __tablename__ = 'event'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=False)


    class Location(Base):
        __tablename__ = 'location'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=True)

        event_id = sa.Column(sa.Integer, sa.ForeignKey(Event.id))
        event = sa.orm.relationship(
            Location,
            backref='locations'  # the event needs to have this
        )


    class LocationForm(ModelForm):
        class Meta:
            model = Location


    class EventForm(ModelForm):
        class Meta:
            model = Event

        locations = ModelFieldList(FormField(LocationForm))

Now if we populate the EventForm, WTForms-Alchemy is smart enough to populate related
locations too. ::

    event = Event()
    form = EventForm(request.POST)
    form.populate_obj(event)
