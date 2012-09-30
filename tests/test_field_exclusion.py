from datetime import datetime
import sqlalchemy as sa
from tests import ModelFormTestCase


class TestFieldExclusion(ModelFormTestCase):
    def test_does_not_include_datetime_columns_with_default(self):
        self.init(sa.DateTime, default=datetime.now())
        assert not self.has_field('test_column')

    def test_excludes_surrogate_primary_keys_by_default(self):
        self.init()
        assert not self.has_field('id')
