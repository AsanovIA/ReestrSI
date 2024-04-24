from src.mixins import (
    SettingsMixin, IndexMixin, ListMixin, ChangeMixin, AddMixin, DeleteMixin
)
from src.users.models import *


class IndexView(IndexMixin):
    pass


class ListObjectView(SettingsMixin, ListMixin):
    pass


class ChangeObjectView(SettingsMixin, ChangeMixin):
    pass


class AddObjectView(SettingsMixin, AddMixin):
    form_class_name = 'AddUserForm'


class DeleteObjectView(SettingsMixin, DeleteMixin):
    pass
