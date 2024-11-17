import sqlalchemy as sa

from tests import FormRelationsTestCase
from wtforms_alchemy import utils


class TestUtils(FormRelationsTestCase):
    def create_models(self):
        class Band(self.base):
            __tablename__ = "band"
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)

        class Person(self.base):
            __tablename__ = "person"
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)

        class BandMember(self.base):
            __tablename__ = "band_members"
            band_id = sa.Column(sa.Integer, sa.ForeignKey(Band.id), primary_key=True)
            band = sa.orm.relationship(Band, backref="members")
            person_id = sa.Column(
                sa.Integer, sa.ForeignKey(Person.id), primary_key=True
            )
            person = sa.orm.relationship(
                Person, backref=sa.orm.backref("band_role", uselist=False)
            )
            role = sa.Column(sa.Unicode(255), nullable=False)

            def __repr__(self):
                fmt = "<BandMember band_id={} person_id={} at {:x}>"
                return fmt.format(repr(self.band_id), repr(self.person_id), id(self))

        self.Band = Band
        self.Person = Person
        self.BandMember = BandMember

    def create_forms(self):
        pass

    def test_find_entity(self):
        band = self.Band(name="The Furious")
        self.session.add(band)
        singer = self.Person(name="Paul Insane")
        self.session.add(self.BandMember(band=band, person=singer, role="singer"))
        guitarist = self.Person(name="John Crazy")
        self.session.add(self.BandMember(band=band, person=guitarist, role="guitar"))
        self.session.commit()

        sing_data = dict(band_id=band.id, person_id=singer.id, role="singer")
        guitar_data = dict(band_id=band.id, person_id=guitarist.id, role="guitar")

        assert (
            utils.find_entity(band.members, self.BandMember, sing_data)
            is singer.band_role
        )
        assert (
            utils.find_entity(band.members, self.BandMember, guitar_data)
            is guitarist.band_role
        )
