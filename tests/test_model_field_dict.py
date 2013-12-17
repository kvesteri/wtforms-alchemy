# from pytest import raises

# import sqlalchemy as sa
# from sqlalchemy.orm.collections import attribute_mapped_collection
# from wtforms_alchemy import ModelForm, ModelFieldDict
# from wtforms_alchemy.fields import FieldDict
# from wtforms import Form
# from wtforms.fields import FormField, StringField
# from tests import FormRelationsTestCase, MultiDict


# class FieldDict(FieldList):
#     """Acts just like a FieldList, but works with a `dict` instead of
#     a `list`. Also, it wouldn't make sense to have `min_entries` and
#     `max_entries` params, so they are not provided.

#     The `keys` of the `dict` are used as labels for the generated
#     fields.

#     Warning: the character '-' must not be used in the `keys` of the
#     `dict` because it is already used to separate the parts of the
#     names/ids of the form fields. This should be configurable but
#     it would require a lot of changes in WTForms.
#     """
#     def __init__(self, unbound_field, label=None, validators=None,
#                  default=dict, **kwargs):
#         super(FieldDict, self).__init__(
#             unbound_field, label,
#             validators, min_entries=0, max_entries=None,
#             default=default, **kwargs
#         )

#     def process(self, formdata, data=_unset_value):

#         self.entries = []
#         if data is _unset_value or not data:
#             try:
#                 data = self.default()
#             except TypeError:
#                 data = self.default

#         self.object_data = data

#         if formdata:
#             indices = sorted(set(self._extract_indices(self.name, formdata)))

#             for index in indices:
#                 try:
#                     obj_data = data[index]
#                 except KeyError:
#                     obj_data = _unset_value
#                 self._add_entry(formdata, obj_data, index=index)
#         else:
#             for index, obj_data in data.items():
#                 self._add_entry(formdata, obj_data, index)

#     def _extract_indices(self, prefix, formdata):
#         offset = len(prefix) + 1
#         for k in formdata:
#             if k.startswith(prefix):
#                 k = k[offset:].split('-', 1)[0]
#                 yield k

#     def _add_entry(self, formdata=None, data=_unset_value, index=None):
#         name = '{}-{}'.format(self.short_name, index)
#         id = '{}-{}'.format(self.id, index)

#         field = self.unbound_field.bind(label=index, form=None, name=name,
#                                         prefix=self._prefix, id=id)
#         field.process(formdata, data)
#         self.entries.append(field)
#         return field

#     def append_entry(self, data=None):
#         if not data:
#             raise TypeError(
#                 'To add an entry to a FieldDict, you must at '
#                 'least provide a valid `dict`, containing at '
#                 'least one key.'
#             )
#         return self._add_entry(data=data)

#     def populate_obj(self, obj, name):
#         dic = getattr(obj, name, {})
#         _fake = type(str('_fake'), (object, ), {})
#         output = {}

#         for field in self.entries:
#             id = self._extract_entry_id(field)
#             fake_obj = _fake()
#             fake_obj.data = dic.get(id, None)
#             field.populate_obj(fake_obj, 'data')
#             output[id] = fake_obj.data

#         setattr(obj, name, output)

#     @property
#     def data(self):
#         return {self._extract_entry_id(e): e.data for e in self.entries}

#     def _extract_entry_id(self, entry):
#         offset = len(self.id) + 1
#         return entry.id[offset:]


# class TestModelFieldDict(FormRelationsTestCase):
#     def create_models(self):
#         class Item(self.base):
#             __tablename__ = 'item'
#             id = sa.Column(sa.Integer, primary_key=True)
#             name = sa.Column(sa.Unicode(255), nullable=False)

#         class Note(self.base):
#             __tablename__ = 'note'
#             id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

#             keyword = sa.Column(sa.Unicode(255))
#             content = sa.Column(sa.UnicodeText, nullable=True)

#             item_id = sa.Column(sa.Integer, sa.ForeignKey(Item.id))
#             item = sa.orm.relationship(
#                 Item,
#                 backref=sa.orm.backref(
#                     'items',
#                     collection_class=attribute_mapped_collection('keyword'),
#                     cascade="all, delete-orphan"
#                 )
#             )

#         self.Item = Item
#         self.Note = Note

#     def create_forms(self):
#         class NoteForm(ModelForm):
#             class Meta:
#                 model = self.Note

#         class ItemForm(ModelForm):
#             class Meta:
#                 model = self.Item

#             notes = ModelFieldDict(FormField(NoteForm))

#         self.NoteForm = NoteForm
#         self.ItemForm = ItemForm

#     def test_saves_new_entries(self, data={}):
#         class AForm(Form):
#             attributes = FieldDict(StringField())
#             something = StringField()

#         class Resource(object):
#             attributes = {
#                 'anattribute': 'avalue',
#                 'anotherattribute': 'anothervalue'
#             }
#             something = '123'

#         form = AForm(
#             MultiDict(), obj=Resource()
#         )

#         assert 0

