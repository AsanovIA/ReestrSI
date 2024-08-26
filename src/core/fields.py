import datetime
import itertools

from markupsafe import Markup
from wtforms import widgets
from flask_wtf.file import FileField
from wtforms.fields.choices import SelectField
from wtforms.validators import ValidationError

from src.db.repository import Repository
from src.config import settings
from src.core.queries import Query
from . import ALL_VAR
from .utils import get_model
from .widgets import ExtendedFileInput


BLANK_CHOICE = [('', '---------')]
ALL_CHOICE = [(ALL_VAR, 'Не важно')]


def get_choices_for_model(model_name):
    model = get_model(model_name)
    query = Query(model=model, filters=[model.view])
    choices = [
        (str(obj.id), obj) for obj in Repository.task_get_list(q=query)
    ]
    return choices


class ExtendedSelectField(SelectField):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.choices = BLANK_CHOICE + get_choices_for_model(model)


class FilterField:
    widget = None

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.id = kwargs.get('id')

    def __call__(self, **kwargs):
        return self.widget(self, **kwargs)


class FilterSelectField(FilterField):
    widget = widgets.Select()

    def __init__(self, model=None, **kwargs):
        super().__init__(**kwargs)
        self.data = kwargs.get('data')
        choices = kwargs.get('choices')
        if choices is None and model is not None:
            choices = BLANK_CHOICE + get_choices_for_model(model)
        self.choices = ALL_CHOICE + choices

    def iter_choices(self):
        if not self.choices:
            choices = []
        elif isinstance(self.choices, dict):
            choices = list(itertools.chain.from_iterable(self.choices.values()))
        else:
            choices = self.choices

        return self._choices_generator(choices)

    def has_groups(self):
        return False

    def _choices_generator(self, choices):
        if not choices:
            _choices = []

        elif isinstance(choices[0], (list, tuple)):
            _choices = choices

        else:
            _choices = zip(choices, choices)

        for value, label in _choices:
            yield value, label, value == self.data


class FilterDateField(FilterField):
    widget = widgets.DateInput()
    format = "%Y-%m-%d"

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        try:
            self.data = datetime.datetime.strptime(data, self.format).date()
        except ValueError:
            self.data = None

    def _value(self):
        return self.data and self.data.strftime(self.format) or ""


class ExtendedFileField(FileField):
    widget = ExtendedFileInput()

    def __init__(self, description=None, **kwargs):
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        self.max_length = settings.MAX_CONTENT_LENGTH
        self.allowed_symbols = settings.ALLOWED_SYMBOLS_CONTENT
        if description is None:
            description = self.set_description()
        self.filename = None
        self.filehash = None
        super().__init__(description=description, **kwargs)

    def set_description(self):
        descriptions = [
            f'Допустимые символы в имени файла: '
            f'{", ".join(self.allowed_symbols)}',
            f'Допустимые расширения файлов: '
            f'{", ".join(self.allowed_extensions)}',
            f'Максимальная длинна имени файла {self.max_length}.'
        ]
        text = ''.join(
            '<li>{}</li>'.format(description) for description in descriptions
        )

        return Markup('<ul>{}</ul>'.format(text))

    def post_validate(self, form, validation_stopped):
        filename = getattr(self.data, 'filename', None)
        if filename:
            if '.' not in filename:
                raise ValidationError('Отсутствует расширение файла')
            basename, extension = filename.rsplit('.', 1)
            self.allow_extension(extension)
            self.length_filename(basename)

        return validation_stopped

    def allow_extension(self, extension):
        if extension.lower() in self.allowed_extensions:
            return

        raise ValidationError(
            f'расширение файла "{extension}" не допустимо.'
        )

    def length_filename(self, filename):
        if len(filename) < self.max_length:
            return

        raise ValidationError(
            f'Имя файла не должно содержать более {self.max_length} символов.'
        )
