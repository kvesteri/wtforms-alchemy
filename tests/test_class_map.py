from pytest import mark, raises

from wtforms_alchemy.utils import ClassMap


class A:
    pass


class B:
    pass


class A2(A):
    pass


class A3(A2):
    pass


class A4(A3):
    pass


class A5(A4):
    pass


class B2(B):
    pass


class C:
    pass


@mark.parametrize("key", [B2, B, A, A2])
def test_contains_with_subclass_check(key):
    class_map = ClassMap({A: 3, B: 6})
    assert key in class_map


@mark.parametrize("key", [B2(), B(), A(), A2()])
def test_contains_with_isinstance_check(key):
    class_map = ClassMap({A: 3, B: 6})
    assert key in class_map


@mark.parametrize(("key", "value"), [(B2, 6), (B, 6), (A, 3), (A2, 3)])
def test_getitem_with_classes(key, value):
    class_map = ClassMap({A: 3, B: 6})
    assert class_map[key] == value


@mark.parametrize(("key", "value"), [(B2(), 6), (B(), 6), (A(), 3), (A2(), 3)])
def test_getitem_with_objects(key, value):
    class_map = ClassMap({A: 3, B: 6})
    assert class_map[key] == value


def test_getitem_throws_keyerror_for_unknown_key():
    class_map = ClassMap({A: 3, B: 6})
    with raises(KeyError):
        class_map["unknown"]
