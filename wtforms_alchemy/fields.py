import six
from wtforms.fields import FieldList, FormField
from .exc import UnknownIdentityException
from .utils import has_entity


class SkipOperation(Exception):
    pass


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
            population_strategy='replace',
            **kwargs):
        self.population_strategy = population_strategy
        super(ModelFieldList, self).__init__(unbound_field, **kwargs)

    def pre_append_object(self, obj, name, counter):
        pass

    def populate_obj(self, obj, name):
        model = self.unbound_field.args[0].Meta.model
        state = obj._sa_instance_state

        if not state.identity or self.population_strategy == 'replace':
            setattr(obj, name, [])
            for counter in six.moves.range(len(self.entries)):
                try:
                    self.pre_append_object(obj, name, counter)
                    try:
                        getattr(obj, name).append(model())
                    except AttributeError:
                        pass
                except SkipOperation:
                    pass
        else:
            for index, entry in enumerate(self.entries):
                data = entry.data
                try:
                    if not has_entity(obj, name, model, data):
                        getattr(obj, name).insert(index, model())
                except UnknownIdentityException:
                    getattr(obj, name).insert(index, model())
        FieldList.populate_obj(self, obj, name)
