from flask_login import UserMixin
from flask import g

from src.db.repository import Repository
from src.core.utils import get_model


class UserLogin(UserMixin):
    is_active_user = True
    id = None

    @property
    def is_active(self):
        return self.is_active_user

    def get_user(self, pk):
        g.model = get_model('userprofile')
        result = Repository.task_get_object(pk)
        if result:
            self.id = result.id
            self.is_active_user = result.is_active

        return self

    def create(self, user):
        self.id = user.id
        self.is_active_user = user.is_active
        return self
