from flask import g

from src.core import Query
from src.core.mixins import (
    SettingsMixin, IndexMixin, ListMixin, ChangeMixin, AddMixin, DeleteMixin
)


class IndexView(IndexMixin):
    pass


class ListObjectView(SettingsMixin, ListMixin):
    def get_query(self, query=None):
        query = super().get_query(query)
        if not g.user.is_superuser:
            query += Query(filters=[~g.model.is_superuser])

        return query


class ChangeObjectView(SettingsMixin, ChangeMixin):
    pass


class AddObjectView(SettingsMixin, AddMixin):
    form_class_name = 'AddUserForm'


class DeleteObjectView(SettingsMixin, DeleteMixin):
    pass


class AdminPasswordChangeView(SettingsMixin, ChangeMixin):
    form_class_name = 'AdminPasswordChangeForm'
    template = 'password_set.html'

    def get_btn(self):
        return {'btn_change': True, 'btn_text': 'Изменить пароль'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = str(g.object)
        return context
