import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import close_all_sessions
from wtforms import Form

from wtforms_alchemy import (
    GroupedQuerySelectField,
    GroupedQuerySelectMultipleField,
    ModelForm,
    QuerySelectField,
    QuerySelectMultipleField,
)


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


class LazySelect:
    def __call__(self, field, **kwargs):
        return list(
            (val, str(label), selected)
            for val, label, selected, _ in field.iter_choices()
        )


class Base:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestBase:
    def create_models(self):
        class Test(self.base):
            __tablename__ = "test"
            id = sa.Column(sa.Integer, primary_key=True, nullable=False)
            name = sa.Column(sa.String, nullable=False)

        self.Test = Test

        class PKTest(self.base):
            __tablename__ = "pk_test"
            foobar = sa.Column(sa.String, primary_key=True, nullable=False)
            baz = sa.Column(sa.String, nullable=False)

            def __str__(self):
                return self.baz

        self.PKTest = PKTest

    def _fill(self, sess):
        for i, n in [(1, "apple"), (2, "banana")]:
            s = self.Test(id=i, name=n)
            p = self.PKTest(foobar=f"hello{i}", baz=n)
            sess.add(s)
            sess.add(p)
        sess.flush()
        sess.commit()


class TestQuerySelectField(TestBase):
    def setup_method(self):
        self.engine = sa.create_engine("sqlite:///:memory:", echo=False)

        self.base = declarative_base()
        self.create_models()

        self.base.metadata.create_all(self.engine)

        Session = sa.orm.session.sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self):
        close_all_sessions()
        self.base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_without_factory(self):
        self._fill(self.session)

        class F(Form):
            a = QuerySelectField(
                get_label="name", widget=LazySelect(), get_pk=lambda x: x.id
            )

        form = F(DummyPostData(a=["1"]))
        form.a.query = self.session.query(self.Test)
        assert form.a.data is not None
        assert form.a.data.id, 1
        assert form.a(), [("1", "apple", True), ("2", "banana", False)]
        assert form.validate()

        form = F(a=self.session.query(self.Test).filter_by(name="banana").first())
        form.a.query = self.session.query(self.Test).filter(self.Test.name != "banana")
        assert not form.validate()
        assert form.a.errors, ["Not a valid choice"]

        # Test query with no results
        form = F()
        form.a.query = (
            self.session.query(self.Test)
            .filter(self.Test.id == 1, self.Test.id != 1)
            .all()
        )
        assert form.a() == []

    def test_with_query_factory(self):
        self._fill(self.session)

        class F(Form):
            a = QuerySelectField(
                get_label=(lambda model: model.name),
                query_factory=lambda: self.session.query(self.Test),
                widget=LazySelect(),
            )
            b = QuerySelectField(
                allow_blank=True,
                query_factory=lambda: self.session.query(self.PKTest),
                widget=LazySelect(),
            )

        form = F()
        assert form.a.data is None
        assert form.a() == [("1", "apple", False), ("2", "banana", False)]
        assert form.b.data is None
        assert form.b() == [
            ("__None", "", True),
            ("hello1", "apple", False),
            ("hello2", "banana", False),
        ]
        assert not form.validate()

        # Test query with no results
        form = F()
        form.a.query = (
            self.session.query(self.Test)
            .filter(self.Test.id == 1, self.Test.id != 1)
            .all()
        )
        assert form.a() == []

        form = F(DummyPostData(a=["1"], b=["hello2"]))
        assert form.a.data.id == 1
        assert form.a() == [("1", "apple", True), ("2", "banana", False)]
        assert form.b.data.baz == "banana"
        assert form.b() == [
            ("__None", "", False),
            ("hello1", "apple", False),
            ("hello2", "banana", True),
        ]
        assert form.validate()

        # Make sure the query is cached
        self.session.add(self.Test(id=3, name="meh"))
        self.session.flush()
        self.session.commit()
        assert form.a() == [("1", "apple", True), ("2", "banana", False)]
        form.a._object_list = None
        assert form.a() == [
            ("1", "apple", True),
            ("2", "banana", False),
            ("3", "meh", False),
        ]

        # Test bad data
        form = F(DummyPostData(b=["__None"], a=["fail"]))
        assert not form.validate()
        assert form.a.errors == ["Not a valid choice"]
        assert form.b.errors == []
        assert form.b.data is None


class TestQuerySelectMultipleField(TestBase):
    def setup_method(self):
        self.engine = sa.create_engine("sqlite:///:memory:", echo=False)

        self.base = declarative_base()
        self.create_models()

        self.base.metadata.create_all(self.engine)

        Session = sa.orm.session.sessionmaker(bind=self.engine)
        self.session = Session()

        self._fill(self.session)

    def teardown_method(self):
        close_all_sessions()
        self.base.metadata.drop_all(self.engine)
        self.engine.dispose()

    class F(Form):
        a = QuerySelectMultipleField(get_label="name", widget=LazySelect())

    def test_unpopulated_default(self):
        form = self.F()
        assert [] == form.a.data

    def test_single_value_without_factory(self):
        form = self.F(DummyPostData(a=["1"]))
        form.a.query = self.session.query(self.Test)
        assert [1] == [v.id for v in form.a.data]
        assert form.a() == [("1", "apple", True), ("2", "banana", False)]
        assert form.validate()

    def test_multiple_values_without_query_factory(self):
        form = self.F(DummyPostData(a=["1", "2"]))
        form.a.query = self.session.query(self.Test)
        assert [1, 2] == [v.id for v in form.a.data]
        assert form.a() == [("1", "apple", True), ("2", "banana", True)]
        assert form.validate()

        form = self.F(DummyPostData(a=["1", "3"]))
        form.a.query = self.session.query(self.Test)
        assert [x.id for x in form.a.data], [1]
        assert not form.validate()

    def test_single_default_value(self):
        first_test = self.session.get(self.Test, 2)

        class F(Form):
            a = QuerySelectMultipleField(
                get_label="name",
                default=[first_test],
                widget=LazySelect(),
                query_factory=lambda: self.session.query(self.Test),
            )

        form = F()
        assert [v.id for v in form.a.data], [2]
        assert form.a(), [("1", "apple", False), ("2", "banana", True)]
        assert form.validate()

    def test_empty_query(self):
        # Test query with no results
        form = self.F()
        form.a.query = (
            self.session.query(self.Test)
            .filter(self.Test.id == 1, self.Test.id != 1)
            .all()
        )
        assert form.a() == []


class DatabaseTestCase:
    def setup_method(self, method):
        self.engine = sa.create_engine("sqlite:///:memory:")

        self.base = declarative_base()
        self.create_models()

        self.base.metadata.create_all(self.engine)

        Session = sa.orm.session.sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        close_all_sessions()
        self.base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_models(self):
        class City(self.base):
            __tablename__ = "city"
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.String)
            country = sa.Column(sa.String)
            state_id = sa.Column(sa.Integer, sa.ForeignKey("state.id"))

        self.City = City

        class State(self.base):
            __tablename__ = "state"
            id = sa.Column(sa.Integer, primary_key=True)
            cities = sa.orm.relationship("City")

        self.State = State

    def create_cities(self):
        self.session.add_all(
            [
                self.City(name="Helsinki", country="Finland"),
                self.City(name="Vantaa", country="Finland"),
                self.City(name="New York", country="USA"),
                self.City(name="Washington", country="USA"),
                self.City(name="Stockholm", country="Sweden"),
            ]
        )


class TestGroupedQuerySelectField(DatabaseTestCase):
    def create_form(self, **kwargs):
        query = self.session.query(self.City).order_by("name", "country")

        class MyForm(Form):
            city = GroupedQuerySelectField(
                label=kwargs.get("label", "City"),
                query_factory=kwargs.get("query_factory", lambda: query),
                get_label=kwargs.get("get_label", lambda c: c.name),
                get_group=kwargs.get("get_group", lambda c: c.country),
                allow_blank=kwargs.get("allow_blank", False),
                blank_text=kwargs.get("blank_text", ""),
                blank_value=kwargs.get("blank_value", "__None"),
            )

        return MyForm

    def test_custom_none_value(self):
        self.create_cities()
        MyForm = self.create_form(
            allow_blank=True, blank_text="Choose city...", blank_value=""
        )
        form = MyForm(DummyPostData({"city": ""}))
        assert form.validate(), form.errors
        assert '<option selected value="">Choose city...</option>' in (str(form.city))

    def test_rendering(self):
        MyForm = self.create_form()
        self.create_cities()
        assert str(MyForm().city).replace("\n", "") == (
            '<select id="city" name="city">'
            '<optgroup label="Finland">'
            '<option value="1">Helsinki</option>'
            '<option value="2">Vantaa</option>'
            '</optgroup><optgroup label="Sweden">'
            '<option value="5">Stockholm</option>'
            "</optgroup>"
            '<optgroup label="USA">'
            '<option value="3">New York</option>'
            '<option value="4">Washington</option>'
            "</optgroup>"
            "</select>"
        )


class TestGroupedQuerySelectMultipleField(DatabaseTestCase):
    def create_form(self, **kwargs):
        query = self.session.query(self.City).order_by("name", "country")

        class MyForm(ModelForm):
            class Meta:
                model = self.State

            cities = GroupedQuerySelectMultipleField(
                label=kwargs.get("label", "City"),
                query_factory=kwargs.get("query_factory", lambda: query),
                get_label=kwargs.get("get_label", lambda c: c.name),
                get_group=kwargs.get("get_group", lambda c: c.country),
                blank_text=kwargs.get("blank_text", ""),
            )

        return MyForm

    def test_unpopulated_default(self):
        MyForm = self.create_form()
        self.create_cities()
        assert MyForm().cities.data == []

    def test_single_value_without_factory(self):
        obj = self.State()
        MyForm = self.create_form()
        self.create_cities()
        form = MyForm(DummyPostData(cities=["1"]), obj=obj)
        assert [1] == [v.id for v in form.cities.data]
        assert form.validate()
        form.populate_obj(obj)
        assert [city.id for city in obj.cities] == [1]

    def test_multiple_values_without_query_factory(self):
        obj = self.State()
        MyForm = self.create_form()
        self.create_cities()
        form = MyForm(DummyPostData(cities=["1", "2"]), obj=obj)
        form.cities.query = self.session.query(self.City)

        assert [1, 2] == [v.id for v in form.cities.data]
        assert form.validate()
        form.populate_obj(obj)
        assert [city.id for city in obj.cities] == [1, 2]

        form = MyForm(DummyPostData(cities=["1", "666"]))
        form.cities.query = self.session.query(self.City)
        assert not form.validate()
        assert [x.id for x in form.cities.data] == [1]
        assert not form.validate()
        form.populate_obj(obj)
        assert [city.id for city in obj.cities] == [1]

        form = MyForm(DummyPostData(cities=["666"]))
        form.cities.query = self.session.query(self.City)
        assert not form.validate()
        assert [x.id for x in form.cities.data] == []
        assert not form.validate()
        form.populate_obj(obj)
        assert [city.id for city in obj.cities] == []

    def test_rendering(self):
        MyForm = self.create_form()
        self.create_cities()
        assert str(MyForm().cities).replace("\n", "") == (
            '<select id="cities" multiple name="cities">'
            '<optgroup label="Finland">'
            '<option value="1">Helsinki</option>'
            '<option value="2">Vantaa</option>'
            '</optgroup><optgroup label="Sweden">'
            '<option value="5">Stockholm</option>'
            "</optgroup>"
            '<optgroup label="USA">'
            '<option value="3">New York</option>'
            '<option value="4">Washington</option>'
            "</optgroup>"
            "</select>"
        )
