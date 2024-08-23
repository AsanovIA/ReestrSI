import datetime
import hashlib
import os
from functools import lru_cache

from importlib import import_module
from flask import abort, g, url_for
from markupsafe import Markup
from sqlalchemy import Boolean, String
from sqlalchemy.orm import InstrumentedAttribute
from werkzeug.routing import BuildError

from src.config import settings
from src.core.constants import EMPTY_VALUE_DISPLAY

DATE_FORMAT = "%d.%m.%Y"
FIELDS_EXCLUDE = ['csrf_token']
SETTINGS_APPS = {
    'datasource': 'src.datasource',
    'users': 'src.users',
}


def boolean_icon(field_val):
    display = {True: "yes", False: "no", None: "unknown"}[field_val]
    url = url_for('static', filename="img/icon-%s.svg" % display)
    return format_html('<img src="{}" alt="{}">', url, display)


def calculate_file_hash(file, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    for chunk in iter(lambda: file.read(4096), b""):
        hash_func.update(chunk)
    file.seek(0)
    return hash_func.hexdigest()


def convert_quoted_string(s):
    quote = s[0]
    return s[1:-1].replace(r"\%s" % quote, quote).replace(r"\\", "\\")


def display_for_field(value, field, empty_value_display):
    if hasattr(field, 'type') and isinstance(field.type, Boolean):
        return boolean_icon(value)
    elif value is None:
        return empty_value_display
    elif (
            isinstance(field.type, String)
            and field.info.get('type') == 'FileField'
    ):
        upload = field.info.get('upload')
        path_file = os.path.join(upload, value)
        url = try_get_url('source.view_file', filename=path_file)
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)
    else:
        return display_for_value(value, empty_value_display)


def display_for_value(value, empty_value_display, boolean=False):
    if boolean:
        return boolean_icon(value)
    elif value is None:
        return empty_value_display
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, datetime.date):
        return datetime.datetime.strftime(value, DATE_FORMAT)
    elif isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    elif isinstance(value, Markup):
        return value
    else:
        return str(value)


def format_html(format_string, *args, **kwargs):
    args_safe = map(Markup.escape, args)
    kwargs_safe = {k: Markup.escape(v) for (k, v) in kwargs.items()}
    return Markup(format_string.format(*args_safe, **kwargs_safe))


@lru_cache()
def get_app_settings(app_name: str):
    try:
        module = import_module(f'{app_name}.config')
        return getattr(module, 'app_settings')
    except (ModuleNotFoundError, AttributeError):
        raise AttributeError(
            f'Отсутствует конфигурация для приложения {app_name}')


def get_form_class(model=None):
    model = model or g.model
    form_class_name = g.form_class_name or model.__name__ + "Form"
    for app_name in settings.APPS:
        try:
            module = import_module(f'{app_name}.forms')
            form_class = getattr(module, form_class_name)

            return form_class

        except (ModuleNotFoundError, AttributeError):
            continue

    abort(404)


def get_model(model_name: str):
    model_name = model_name.lower().replace('_', '')
    for app_name in settings.APPS:
        try:
            app_settings = get_app_settings(app_name)
            model = app_settings['models'].get(model_name)
            if model:
                return model
        except (ModuleNotFoundError, KeyError, AttributeError):
            continue

    abort(404)


def get_suffix(text: str, n: int):
    from src.core.suffixes import update_suffix

    number = (
        0 if n % 10 == 1 and n % 100 != 11 else 1
        if 2 <= n % 10 <= 4 and (n % 100 < 12 or n % 100 > 14) else 2
    )
    new_text = update_suffix[(text, number)]

    return new_text


def label_for_field(name, model=None, form=None):
    model = model or g.model
    try:
        field = getattr(model, name)
        label = field.info.get('label')
        if label is None:
            field = getattr(model, f'{name}_id')
            label = field.info['label']
    except (AttributeError, KeyError):
        if name == "__str__":
            label = str(model.Meta.verbose_name)
        else:
            if callable(name):
                attr = name
            elif hasattr(g.view, name):
                attr = getattr(g.view, name)
            elif hasattr(model, name):
                attr = getattr(model, name)
            elif hasattr(form, name):
                attr = getattr(form, name)
                return attr.label.text
            else:
                raise AttributeError(
                    f'Не верно указано поле {name} в "fields_display" для '
                    f'модели {model.__name__}'
                )

            if hasattr(attr, "short_description"):
                label = attr.short_description
            elif (
                    isinstance(attr, property)
                    and hasattr(attr, "fget")
                    and hasattr(attr.fget, "short_description")
            ):
                label = attr.fget.short_description
            else:
                label = name

    return label


def lookup_field(name, obj):
    try:
        f = getattr(g.model, name)
        if not isinstance(f, InstrumentedAttribute):
            raise AttributeError
    except AttributeError:
        if callable(name):
            attr = name
            value = attr(obj)
        else:
            attr = getattr(obj, name)
            if callable(attr):
                value = attr()
            else:
                value = attr
        f = None
    else:
        attr = None
        value = getattr(obj, name)
    return f, attr, value


def value_for_field(field_name, obj):
    fields = field_name.split('__') if '__' in field_name else [field_name]
    value = f = None
    if fields and len(fields) > 1:
        model = get_model(fields[-2])
        f = getattr(model, fields[-1])
    for field in fields:
        value = getattr(obj, field, None)
        if not value:
            break
        obj = value

    if f and hasattr(f, 'type'):
        value = display_for_field(value, f, EMPTY_VALUE_DISPLAY)

    return value


def try_get_url(endpoint: str, **kwargs):
    try:
        return url_for(endpoint, **kwargs)
    except BuildError:
        return ''


def upload_for_field(name: str):
    model = g.model
    try:
        field = getattr(model, name)
        if 'type' not in field.info:
            raise KeyError(
                f'отсутствует ключ "type" у атрибута '
                f'{name} модели {model.__name__}'
            )
        return field.info['upload']
    except AttributeError:
        raise AttributeError(
            f'отсутствует атрибут {name} модели {model.__name__}'
        )
    except KeyError:
        raise KeyError(
            f'отсутствует ключ "upload" у атрибута '
            f'{name} модели {model.__name__}'
        )
