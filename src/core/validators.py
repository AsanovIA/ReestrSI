from flask import g
from wtforms.validators import ValidationError

from src.db.repository import Repository


class Unique:
    def __init__(self, message=None):
        if not message:
            message = 'Такая запись уже существует'
        self.message = message

    def __call__(self, form, field):
        model, instance = g.model, g.object
        filters = [
            getattr(model, field.name) == field.data,
            model.id != instance.id,
        ]
        if Repository.task_exists(filters):
            raise ValidationError(self.message)
