from wtforms.fields.choices import SelectField

from src.db.repository import Repository
from .utils import BLANK_CHOICE, get_model


class ExtendedSelectField(SelectField):

    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        options = {'model': get_model(model)}
        choices = [
            (obj.id, obj)
            for obj in Repository.task_get_list(**options)
        ]
        self.choices = BLANK_CHOICE + choices
