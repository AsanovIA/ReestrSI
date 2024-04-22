from src.mixins import (
    ListMixin, ChangeMixin, AddMixin, DeleteMixin
)
from src.admin.models import *


class ListObjectView(ListMixin):
    pass


class ChangeObjectView(ChangeMixin):
    pass


class AddObjectView(AddMixin):
    pass


class DeleteObjectView(DeleteMixin):
    pass
