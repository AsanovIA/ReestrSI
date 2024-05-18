from flask import g
from src.core.mixins import (
    SettingsMixin, IndexMixin, ListMixin, ChangeMixin, AddMixin, DeleteMixin
)


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


class AdminPasswordChangeView(SettingsMixin, ChangeMixin):
    form_class_name = 'AdminPasswordChangeForm'
    template = 'password_set.html'

    def get_btn(self):
        return {'btn_change': True, 'btn_text': 'Изменить пароль'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = str(g.object)
        return context
