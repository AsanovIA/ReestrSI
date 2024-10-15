from flask import g
from flask_login import current_user
from werkzeug.datastructures import FileStorage
from wtforms.validators import ValidationError

from src.core import secure_filename
from src.db.repository import Repository


class Unique:
    def __init__(self, message=None):
        if not message:
            message = 'Такая запись уже существует'
        self.message = message

    def __call__(self, form, field):
        model, instance = g.model, form.instance
        filters = [
            getattr(model, field.name) == field.data,
            model.id != instance.id,
        ]
        if Repository.task_exists(filters):
            raise ValidationError(self.message)


class UniqueFile:
    def __init__(self, message=None):
        if not message:
            message = 'Такой файл уже существует'
        self.message = message

    def __call__(self, form, field):
        model, instance = g.model, form.instance
        if not isinstance(field.data, FileStorage):
            return
        filename = secure_filename(field.data.filename)

        filters = [
            model.id != instance.id,
            getattr(model, field.name) == filename
        ]

        if Repository.task_exists(filters):
            raise ValidationError(self.message)


class OldPassword:
    def __init__(self, message=None):
        if not message:
            message = 'Старый пароль неверен'
        self.message = message

    def __call__(self, form, field):
        if not current_user.check_password(field.data):
            raise ValidationError(self.message)
