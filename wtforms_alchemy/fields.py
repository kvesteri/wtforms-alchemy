from sqlalchemy.orm.util import has_identity
from sqlalchemy.orm import object_session
from wtforms.fields import FieldList, FormField


def session(obj):
    session = object_session(obj)
    if not session:
        raise Exception(
            'Object %s is not bound the session. Use session.add() to '
            'add this object into session.' % str(obj)
        )
    return session


class SkipOperation(Exception):
    pass


class ModelFormField(FormField):
    def populate_obj(self, obj, name):
        if has_identity(obj):
            sess = session(obj)
            item = getattr(obj, name, None)
            if item:
                # only delete persistent objects
                if has_identity(item):
                    sess.delete(item)
                elif item in sess:
                    sess.expunge(item)
                setattr(obj, name, None)

        if self.data:
            setattr(obj, name, self.form.Meta.model())

        FormField.populate_obj(self, obj, name)


class ModelFieldList(FieldList):
    def pre_append_object(self, obj, name, counter):
        pass

    def delete_existing(self, obj, name):
        if has_identity(obj):
            sess = session(obj)
            items = getattr(obj, name, set([]))
            while items:
                item = items.pop()
                # only delete persistent objects
                if has_identity(item):
                    sess.delete(item)

    def populate_obj(self, obj, name):
        self.delete_existing(obj, name)

        model = self.unbound_field.args[0].Meta.model
        for counter in xrange(len(self.entries)):
            try:
                self.pre_append_object(obj, name, counter)
                try:
                    getattr(obj, name).append(model())
                except AttributeError:
                    pass
            except SkipOperation:
                pass
        FieldList.populate_obj(self, obj, name)
