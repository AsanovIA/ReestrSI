from flask import g
from src.core import SettingsMixin, ChangeMixin


class UserPasswordChangeView(SettingsMixin, ChangeMixin):
    form_class_name = 'UserPasswordChangeForm'
    template = 'password_change.html'

    def get_btn(self):
        return {'btn_change': True, 'btn_text': 'Изменить пароль'}

    def get_object(self):
        return g.user
