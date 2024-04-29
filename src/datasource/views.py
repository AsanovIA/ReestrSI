from src.core.mixins import (
    SettingsMixin, IndexMixin, ListMixin, ChangeMixin, AddMixin, DeleteMixin
)
from src.datasource.models import *


class IndexView(IndexMixin):
    pass


class ListObjectView(SettingsMixin, ListMixin):
    pass


class ChangeObjectView(SettingsMixin, ChangeMixin):
    pass


class AddObjectView(SettingsMixin, AddMixin):
    pass


class DeleteObjectView(SettingsMixin, DeleteMixin):
    pass
