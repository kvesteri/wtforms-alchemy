import pytest
from wtforms.form import FormMeta

from wtforms_alchemy import (
    model_form_factory,
    model_form_meta_factory,
    ModelFormMeta,
)


class _MetaWithInit(FormMeta):
    def __init__(cls, *args, **kwargs):
        cls.test_attr = "SomeVal"
        FormMeta.__init__(cls, *args, **kwargs)


MetaWithInit = model_form_meta_factory(_MetaWithInit)


class _MetaWithoutInit(FormMeta):
    test_attr = "SomeVal"


MetaWithoutInit = model_form_meta_factory(_MetaWithoutInit)


@pytest.fixture(params=[MetaWithInit, MetaWithoutInit, ModelFormMeta])
def model_form_all(request):
    """Returns one of each possible model form classes with custom and the
    original metaclass."""
    ModelForm = model_form_factory(meta=request.param)
    return ModelForm


@pytest.fixture(params=[MetaWithInit, MetaWithoutInit])
def model_form_custom(request):
    """Returns one of each possible model form classes with custom
    metaclasses."""
    return model_form_factory(meta=request.param)
