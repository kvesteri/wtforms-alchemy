from pytest import mark, raises
from wtforms_alchemy.utils import ClassMap, sorted_classes


class A(object):
    pass


class B(object):
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


class C(object):
    pass


@mark.parametrize(
    'key',
    [B2, B, A, A2]
)
def test_contains_with_subclass_check(key):
    class_map = ClassMap({A: 3, B: 6})
    assert key in class_map


@mark.parametrize(
    'key',
    [B2(), B(), A(), A2()]
)
def test_contains_with_isinstance_check(key):
    class_map = ClassMap({A: 3, B: 6})
    assert key in class_map


@mark.parametrize(
    ('key', 'value'),
    [
        (B2, 6),
        (B, 6),
        (A, 3),
        (A2, 3)
    ]
)
def test_getitem_with_classes(key, value):
    class_map = ClassMap({A: 3, B: 6})
    assert class_map[key] == value


@mark.parametrize(
    ('key', 'value'),
    [
        (B2(), 6),
        (B(), 6),
        (A(), 3),
        (A2(), 3)
    ]
)
def test_getitem_with_objects(key, value):
    class_map = ClassMap({A: 3, B: 6})
    assert class_map[key] == value


@mark.parametrize(
    'items',
    [
        [A, A2, A3, A4, A5],
        [A2, A, A4, A3, A5],
        [A5, A, A4, A3, A2],
    ]
)
def test_sorted_classes_with_reverse(items):
    assert sorted_classes(items, reverse=True) == [A5, A4, A3, A2, A]


@mark.parametrize(
    'items',
    [
        [A, A2, A3, A4, A5],
        [A2, A, A4, A3, A5],
        [A5, A, A4, A3, A2],
    ]
)
def test_sorted_classes_without_reverse(items):
    assert sorted_classes(items) == [A, A2, A3, A4, A5]


def test_getitem_throws_keyerror_for_unknown_key():
    class_map = ClassMap({A: 3, B: 6})
    with raises(KeyError):
        class_map['unknown']


@mark.parametrize(
    'items',
    [
        {A: 1, A2: 2, A3: 3, A4: 4, A5: 5},
        {A2: 2, A: 1, A4: 4, A3: 3, A5: 5},
        {A5: 5, A: 1, A4: 4, A3: 3, A2: 2},
    ]
)
def test_init_sorts_dict_of_items_by_inheritance(items):
    class_map = ClassMap(items)
    assert list(class_map.items()) == [
        (A5, 5), (A4, 4), (A3, 3), (A2, 2), (A, 1)
    ]


@mark.parametrize(
    'items',
    [
        [(A, 1), (A2, 2), (A3, 3), (A4, 4), (A5, 5)],
        [(A2, 2), (A, 1), (A4, 4), (A3, 3), (A5, 5)],
        [(A5, 5), (A, 1), (A4, 4), (A3, 3), (A2, 2)],
    ]
)
def test_init_sorts_items_by_inheritance(items):
    class_map = ClassMap(items)
    assert list(class_map.items()) == [
        (A5, 5), (A4, 4), (A3, 3), (A2, 2), (A, 1)
    ]
