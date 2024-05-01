from markupsafe import Markup
from wtforms.fields.simple import FileField
from wtforms.fields.choices import SelectField
from wtforms.validators import ValidationError

from src.db.repository import Repository
from src.config import settings
from .utils import BLANK_CHOICE, get_model
from .widgets import ExtendedFileInput


class ExtendedSelectField(SelectField):

    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        options = {'model': get_model(model)}
        choices = [
            (obj.id, obj)
            for obj in Repository.task_get_list(**options)
        ]
        self.choices = BLANK_CHOICE + choices


class ExtendedFileField(FileField):
    widget = ExtendedFileInput()
    MAX_LENGTH: int = 100

    def __init__(self, upload, description=None, **kwargs):
        if description is None:
            description = self.set_description()
        super().__init__(description=description, **kwargs)
        self.upload = upload

    def set_description(self):
        descriptions = [
            (
                f'Допустимые расширения файлов: '
                f'{", ".join(settings.ALLOWED_EXTENSIONS)}'
            ),
            f'Максимальная длинна имени файла {self.MAX_LENGTH}.'
        ]
        text = ''.join(
            '<li>{}</li>'.format(description) for description in descriptions
        )

        return Markup('<ul>{}</ul>'.format(text))

    def post_validate(self, form, validation_stopped):
        filename = self.data.filename
        if filename:
            if '.' not in filename:
                raise ValidationError('Отсутствует расширение файла')
            name, extension = filename.rsplit('.', 1)
            self.allowed_extension(extension)
            self.length_file(name)

        return validation_stopped

    def allowed_extension(self, extension):
        if extension.lower() in settings.ALLOWED_EXTENSIONS:
            return

        raise ValidationError(
            f'расширение файла "{extension}" не допустимо.'
        )

    def length_file(self, filename):
        if len(filename) < self.MAX_LENGTH:
            return

        raise ValidationError(
            f'Имя файла не должно содержать более {self.MAX_LENGTH} символов.'
        )
