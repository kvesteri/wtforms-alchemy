import sqlalchemy as sa
from pytest import mark
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.session import close_all_sessions
from sqlalchemy_utils.types import phone_number

from tests import MultiDict
from wtforms_alchemy import ModelForm


class TestCase:
    def setup_method(self, method):
        self.engine = create_engine("sqlite:///:memory:")
        self.Base = declarative_base()

        self.create_models()
        self.Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        close_all_sessions()
        self.Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_models(self):
        class User(self.Base):
            __tablename__ = "user"
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255))
            phone_number = sa.Column(phone_number.PhoneNumberType(country_code="FI"))

        self.User = User


@mark.xfail("phone_number.phonenumbers is None")
class TestPhoneNumbers(TestCase):
    """
    Simple tests to ensure that sqlalchemy_utils.PhoneNumber,
    wtforms_alchemy.PhoneNumberType and sqlalchemy_utils.PhoneNumberField work
    nicely together.
    """

    def setup_method(self, method):
        super().setup_method(method)

        class UserForm(ModelForm):
            class Meta:
                model = self.User

        self.UserForm = UserForm

        super().setup_method(method)
        self.phone_number = phone_number.PhoneNumber("040 1234567", "FI")
        self.user = self.User()
        self.user.name = "Someone"
        self.user.phone_number = self.phone_number
        self.session.add(self.user)
        self.session.commit()

    def test_query_returns_phone_number_object(self):
        queried_user = self.session.query(self.User).first()
        assert queried_user.phone_number == self.phone_number

    def test_phone_number_is_stored_as_string(self):
        result = self.session.execute(
            sa.text("SELECT phone_number FROM user WHERE id=:param"),
            {"param": self.user.id},
        )
        assert result.first()[0] == "+358401234567"

    def test_phone_number_in_form(self):
        form = self.UserForm(
            MultiDict(name="Matti Meikalainen", phone_number="+358401231233")
        )
        form.validate()
        assert len(form.errors) == 0
        assert form.data["phone_number"] == (phone_number.PhoneNumber("+358401231233"))

    def test_empty_phone_number_in_form(self):
        form = self.UserForm(MultiDict(name="Matti Meikalainen", phone_number=""))
        form.validate()
        assert len(form.errors) == 0
        assert form.data["phone_number"] is None
