from src.mixins import ListMixin, ChangeMixin, AddMixin, DeleteMixin
from src.users.models import Users
from src.utils import try_get_url


class UsersMixin:
    model_name = 'users'


class ListObjectView(UsersMixin, ListMixin):
    def get_url_for_result(self, result):
        return try_get_url(f'.change_{self.blueprint_name}', pk=result.id)


class ChangeObjectView(UsersMixin, ChangeMixin):
    pass


class AddObjectView(UsersMixin, AddMixin):
    pass


class DeleteObjectView(UsersMixin, DeleteMixin):
    pass
