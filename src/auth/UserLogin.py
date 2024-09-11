from flask_login import UserMixin
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash

from src.db.repository import Repository
from src.core.utils import get_model


class UserLogin(UserMixin):
    is_active_user = True
    id = None
    password = None

    @property
    def is_active(self):
        return self.is_active_user

    def get_user(self, pk):
        g.model = get_model('userprofile')
        result = Repository.task_get_object(pk)
        if result:
            g.user = result
            self.id = result.id
            self.is_active_user = result.is_active
            self.password = result.password

        return self

    def create(self, user):
        self.id = user.id
        self.is_active_user = user.is_active
        return self

    def hash_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
