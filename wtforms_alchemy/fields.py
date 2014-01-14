from functools import partial
from itertools import chain, repeat
import six
from wtforms.fields import FieldList, FormField
try:
    from wtforms.utils import unset_value as _unset_value
except ImportError:
    from wtforms.fields import _unset_value
from .utils import find_entity


class SkipOperation(Exception):
    pass


# try:
#     from sqlalchemy.orm.util import identity_key
#     has_identity_key = True
# except ImportError:
#     has_identity_key = False

# def get_pk_from_identity(obj):
#     cls, key = identity_key(instance=obj)
#     return ':'.join(map(six.text_type, key))


# def labelize(func):
#     if func is None:
#         return identity
#     elif isinstance(func, six.string_types):
#         return operator.attrgetter(func)
#     return func


# class NoneChoice(object):
#     def __iter__(self):
#         yield '__None', None


# def identity(func):
#     return func


# class QueryChoices(AbstractChoices):
#     def __init__(self, query_factory, get_pk=None, get_label=None):
#         if get_pk is None:
#             if not has_identity_key:
#                 raise Exception(
#                     'The sqlalchemy identity_key function could not be '
#                     'imported.'
#                 )
#             self.get_pk = get_pk_from_identity
#         else:
#             self.get_pk = get_pk

#         self.get_label = labelize(get_label)
#         self.query_factory = query_factory
#         self._object_list = None

#     @property
#     def object_list(self):
#         if self._object_list is None:
#             query = self.query_factory()
#             self._object_list = list(
#                 (six.text_type(self.get_pk(obj)), obj) for obj in query
#             )
#         return self._object_list

#     @property
#     def choices(self):
#         for pk, obj in self.object_list:
#             yield pk, self.get_label(obj), obj


class ModelFormField(FormField):
    def populate_obj(self, obj, name):
        if self.data:
            try:
                if getattr(obj, name) is None:
                    setattr(obj, name, self.form.Meta.model())
            except AttributeError:
                pass
        FormField.populate_obj(self, obj, name)


class ModelFieldList(FieldList):
    def __init__(
            self,
            unbound_field,
            population_strategy='update',
            **kwargs):
        self.population_strategy = population_strategy
        super(ModelFieldList, self).__init__(unbound_field, **kwargs)

    @property
    def model(self):
        return self.unbound_field.args[0].Meta.model

    def _get_bound_field_for_entry(self, formdata, data, index):
        assert not self.max_entries or len(self.entries) < self.max_entries, \
            'You cannot have more than max_entries entries in this FieldList'
        new_index = self.last_index = index or (self.last_index + 1)
        name = '%s-%d' % (self.short_name, new_index)
        id = '%s-%d' % (self.id, new_index)
        if hasattr(self, 'meta'):
            # WTForms 2.0
            return self.unbound_field.bind(
                form=None,
                name=name,
                prefix=self._prefix,
                id=id,
                _meta=self.meta
            )
        else:
            # WTForms 1.0
            return self.unbound_field.bind(
                form=None, name=name, prefix=self._prefix, id=id
            )

    def _add_entry(self, formdata=None, data=_unset_value, index=None):
        field = self._get_bound_field_for_entry(
            formdata=formdata,
            data=data,
            index=index
        )
        if (
            data != _unset_value and
            data
        ):
            if formdata:
                field.process(formdata)
            else:
                field.process(formdata, data=data)

            entity = find_entity(self.object_data, self.model, field.data)
            if entity is not None:
                field.process(formdata, entity)
        else:
            field.process(formdata)

        self.entries.append(field)
        return field

    def populate_obj(self, obj, name):
        state = obj._sa_instance_state

        if not state.identity or self.population_strategy == 'replace':
            setattr(obj, name, [])
            for counter in six.moves.range(len(self.entries)):
                try:
                    getattr(obj, name).append(self.model())
                except AttributeError:
                    pass
        else:
            for index, entry in enumerate(self.entries):
                data = entry.data
                coll = getattr(obj, name)
                if find_entity(coll, self.model, data) is None:
                    coll.insert(index, self.model())
        FieldList.populate_obj(self, obj, name)
