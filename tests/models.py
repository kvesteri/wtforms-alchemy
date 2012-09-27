from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import BigInteger
from wtforms.validators import Email


Base = declarative_base()


class Entity(Base):
    __tablename__ = 'entity'
    id = sa.Column(BigInteger, autoincrement=True, primary_key=True)


class User(Entity):
    __tablename__ = 'user'
    STATUSES = ('status1', 'status2')
    query = None

    id = sa.Column(sa.BigInteger, sa.ForeignKey(Entity.id), primary_key=True)
    name = sa.Column(sa.Unicode(255), index=True, nullable=False, default=u'')
    email = sa.Column(
        sa.Unicode(255),
        unique=True,
        nullable=False,
        info={'validators': Email()}
    )
    status = sa.Column(sa.Enum(*STATUSES))
    status2 = sa.Column(
        sa.Enum(*STATUSES),
        info={
            'choices': {
                'status1': 'some status',
                'status2': 'another status'
            }
        }
    )
    overridable_field = sa.Column(sa.Integer)
    excluded_field = sa.Column(sa.Integer)
    is_active = sa.Column(sa.Boolean)
    age = sa.Column(sa.Integer)
    level = sa.Column(sa.Integer, info={'min': 1, 'max': 100})
    description = sa.Column(sa.Unicode(255))


class Location(Base):
    __tablename__ = 'location'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    name = sa.Column(
        sa.Unicode(255),
        nullable=False,
        info={
            'label': 'Name',
            'description': 'This is name of the location.'
        }
    )
    longitude = sa.Column(sa.Integer)
    latitude = sa.Column(sa.Integer)


class Address(Base):
    __tablename__ = 'address'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    name = sa.Column(
        sa.Unicode(255),
        nullable=False
    )
    location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
    location = sa.orm.relationship(Location, backref='addresses')


class Event(Entity):
    __tablename__ = 'event'
    id = sa.Column(sa.BigInteger, sa.ForeignKey(Entity.id), primary_key=True)
    name = sa.Column(
        sa.Unicode(255), index=True, nullable=False, default=u'',
        info={'label': 'Name', 'description': 'The name of the event.'}
    )
    start_time = sa.Column(sa.DateTime)
    is_private = sa.Column(sa.Boolean, nullable=False)
    description = sa.Column(sa.UnicodeText, default=lambda: '')
    location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
    location = sa.orm.relationship(Location)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    some_enum = sa.Column(sa.Enum('1', '2'))
    unicode_with_choices = sa.Column(
        sa.Unicode(255),
        info={
            'choices': (
                (u'1', u'Choice 1'),
                (u'2', u'Choice 2')
            )
        }
    )
