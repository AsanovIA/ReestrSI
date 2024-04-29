from importlib import import_module
from flask import abort, g, url_for
from markupsafe import Markup
from sqlalchemy import Boolean
from sqlalchemy.orm import InstrumentedAttribute
from werkzeug.routing import BuildError

from src.config import settings

BLANK_CHOICE = [(0, '---------')]
EMPTY_VALUE_DISPLAY = '-'
FIELDS_EXCLUDE = ['csrf_token']
SETTINGS_APP_LIST = [
    'datasource',
    'users',
]


def try_get_url(endpoint: str, **kwargs):
    try:
        return url_for(endpoint, **kwargs)
    except BuildError:
        return ''


def get_app_settings(app_name: str):
    try:
        module = import_module(f'{app_name}.config')
        return getattr(module, 'app_settings')
    except (ModuleNotFoundError, AttributeError):
        raise AttributeError(
            f'Отсутствует конфигурация для приложения {app_name}')


def get_model(model_name: str):
    for app_name in settings.APPS:
        try:
            app_settings = get_app_settings(app_name)
            model = app_settings['models'].get(model_name.lower())
            if model:
                return model
        except (ModuleNotFoundError, KeyError, AttributeError):
            continue

    abort(404)


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


def label_for_field(name):
    try:
        try:
            field = getattr(g.model, name)
            if hasattr(field, 'doc'):
                label = field.doc
            else:
                label = field.property.doc
            if label is None:
                raise AttributeError
        except AttributeError:
            field = getattr(g.form, name)
            label = field.label.text

    except AttributeError:
        if name == "__str__":
            label = str(g.model.Meta.verbose_name)
        else:
            if callable(name):
                attr = name
            elif hasattr(g.view, name):
                attr = getattr(g.view, name)
            elif hasattr(g.model, name):
                attr = getattr(g.model, name)
            else:
                raise AttributeError(
                    f'Не верно указаны поля "fields_display" для модели '
                    f'{g.model.__name__}'
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


def boolean_icon(field_val):
    display = {True: "yes", False: "no", None: "unknown"}[field_val]
    url = url_for('static', filename="img/icon-%s.svg" % display)
    return format_html('<img src="{}" alt="{}">', url, display)


def display_for_field(value, type_field, empty_value_display):
    if isinstance(type_field, Boolean):
        return boolean_icon(value)
    elif value is None:
        return empty_value_display
    else:
        return display_for_value(value, empty_value_display)


def display_for_value(value, empty_value_display, boolean=False):
    if boolean:
        return boolean_icon(value)
    elif value is None:
        return empty_value_display
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    else:
        return str(value)


def format_html(format_string, *args, **kwargs):
    args_safe = map(Markup.escape, args)
    kwargs_safe = {k: Markup.escape(v) for (k, v) in kwargs.items()}
    return Markup(format_string.format(*args_safe, **kwargs_safe))


def get_suffix(text, n):
    from src.core.suffixes import update_suffix

    number = (
        0 if n % 10 == 1 and n % 100 != 11 else 1
        if 2 <= n % 10 <= 4 and (n % 100 < 12 or n % 100 > 14) else 2
    )
    new_text = update_suffix[(text, number)]

    return new_text