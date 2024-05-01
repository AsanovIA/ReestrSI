import os
import datetime
from typing import Union, List, Tuple

from flask import abort, current_app, g, redirect, render_template, request
from flask.views import View
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Relationship
from werkzeug.routing import BuildError
from werkzeug.utils import secure_filename

from src.config import settings
from src.db.repository import Repository
from src.core.media import Media
from src.core.utils import (
    EMPTY_VALUE_DISPLAY,
    display_for_field,
    display_for_value,
    format_html,
    get_app_settings,
    get_form_class,
    get_model,
    label_for_field,
    lookup_field,
    try_get_url,
)


class SiteMixin(View):
    blueprint_name = None
    template = None
    model_name = None
    pk = None
    model = None
    form_class_name = None
    empty_value_display = EMPTY_VALUE_DISPLAY
    sidebar = None

    def __init__(self, blueprint_name, template=None):
        self.blueprint_name = blueprint_name
        if template is not None:
            self.template = template

    def g_init(self):
        if self.model is not None:
            g.model = self.model
        elif self.model_name is not None:
            g.model = get_model(self.model_name)
        if hasattr(g, 'model') and not hasattr(g.model, 'Meta'):
            raise AttributeError(
                f'Отсутствуют метаданные "Meta" в модели {g.model.__name__}'
            )
        g.view = self
        g.form_class_name = self.form_class_name

    def dispatch_request(self, **kwargs):
        if self.model_name is None:
            self.model_name = kwargs.get('model_name')
        if self.pk is None:
            self.pk = kwargs.get('pk')

        self.g_init()

        if request.method == 'POST':
            return self.post(**kwargs)
        elif request.method == 'GET':
            return self.get(**kwargs)

    def get(self, **kwargs):
        context = self.get_context_data(**kwargs)
        return render_template(self.template, **context)

    def post(self, **kwargs):
        raise NotImplementedError(
            f"не определен метод post() для {self.__class__.__name__}"
        )

    def get_btn(self):
        return {}

    def get_context_data(self, **kwargs):
        context = {
            'title': settings.SITE_NAME,
            'sidebar': self.sidebar,
            'perm': {'perm_change': False},
            'media': self.get_media(),
        }
        if 'admin' in request.blueprints:
            if hasattr(g.model.Meta, 'verbose_name_change'):
                object_verbose_name = g.model.Meta.verbose_name_change
            elif hasattr(g.model.Meta, 'verbose_name'):
                object_verbose_name = g.model.Meta.verbose_name
            else:
                object_verbose_name = ''

            context.update({
                'main_menu': self.get_admin_main_menu(),
                'perm': {
                    'perm_add': True, 'perm_delete': True, 'perm_change': True,
                },
                'btn': self.get_btn(),
                'object_verbose_name': object_verbose_name,
            })
        kwargs.update(context)

        return kwargs

    def get_media(self):
        media = Media()

        return media

    @classmethod
    def get_admin_main_menu(cls):
        main_menu = [
            {
                'title': 'Средства измерения',
                'url': try_get_url('admin.si.list_si')
            },
            {
                'title': 'Обслуживание',
                'url': try_get_url('admin.service.list_service')
            },
            {
                'title': 'Настройки',
                'url': try_get_url('admin.settings.index')
            },
        ]
        return main_menu

    @staticmethod
    def get_app_list(label=None):
        """Список моделей БД для заглавной страницы и боковой панели"""
        from src.core.utils import SETTINGS_APP_LIST

        app_list = []
        settings_app_list = SETTINGS_APP_LIST

        if label:
            settings_app_list = [label]

        for app_label in settings_app_list:
            app_settings = get_app_settings(app_label)
            model_list = []
            for model_name, model in app_settings['models'].items():
                kwargs = {'model_name': model_name}
                model_dict = {
                    'name': model_name,
                    'vnp': model.Meta.verbose_name_plural,
                    'list_url': try_get_url(
                        f'admin.settings.{app_label}.list_{app_label}',
                        **kwargs,
                    ),
                    'add_url': try_get_url(
                        f'admin.settings.{app_label}.add_{app_label}',
                        **kwargs,
                    ),
                }

                model_list.append(model_dict)

            model_list.sort(key=lambda x: x["vnp"].lower())

            app_dict = {
                "name": app_settings.get('verbose_name', app_label),
                "app_label": app_label,
                "app_url": try_get_url(f'admin.settings.{app_label}.index'),
                "models": model_list,
            }
            app_list.append(app_dict)

        return app_list


class SettingsMixin(SiteMixin):
    sidebar = 'menu_sidebar'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_list'] = self.get_app_list()

        return context


class IndexMixin(SiteMixin):
    template = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_list'] = self.get_app_list(self.blueprint_name)

        return context


class ListMixin(SiteMixin):
    template: str = 'list_result.html'
    fields_display: Union[List[str], Tuple[str]] = ()
    fields_link: Union[List[str], Tuple[str], None] = ()
    per_page: int = 20

    def g_init(self):
        super().g_init()
        if self.fields_display:
            g.fields_display = self.fields_display
        elif hasattr(g.model.Meta, 'fields_display'):
            g.fields_display = g.model.Meta.fields_display
        else:
            raise ValueError(
                f'Не указан список полей "fields_display" отображения для '
                f'модели {g.model.__name__}'
            )

        if self.fields_link is None or self.fields_link:
            g.fields_link = self.fields_link
        else:
            g.fields_link = getattr(g.model.Meta, 'fields_link', ())

        g.form = get_form_class()()

    def get_btn(self):
        return {'btn_add': True}

    def get_add_url(self):
        return try_get_url(
            f'.add_{self.blueprint_name}', model_name=self.model_name
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = self.per_page
        offset = (page - 1) * per_page
        filters = {'limit': per_page, 'offset': offset}
        result_list = self.get_queryset(**filters)
        context['pagination'] = self.get_paginator(
            page=page, per_page=per_page
        )
        context['result_headers'] = list(self.get_result_headers())
        context['results'] = list(self.get_results(result_list))
        context['add_url'] = self.get_add_url()
        try:
            context['title'] = g.model.Meta.verbose_name_plural
        except AttributeError:
            pass

        return context

    def get_query(self, **kwargs):
        return kwargs

    def get_queryset(self, **kwargs):
        queryset = Repository.task_get_list(**self.get_query(**kwargs))
        return queryset

    @classmethod
    def get_paginator(cls, page: int, per_page: int) -> Pagination:
        total = Repository.task_count()
        return Pagination(
            page=page,
            per_page=per_page,
            total=total,
            display_msg="показано <b>{start} - {end}</b> записей из"
                        " <b>{total}</b>",
            search_msg='',
            css_framework='bootstrap5',
        )

    @staticmethod
    def get_result_headers():
        """Создание заголовков столбцов таблицы"""

        for field_name in g.fields_display:
            if '.' in field_name:
                field_name = field_name.split('.')[-1]
            text = label_for_field(field_name)

            yield {"text": text}

    def get_results(self, result_list):
        """Заполнение таблицы"""
        for res in result_list:
            yield list(self.items_for_result(res))

    def get_url_for_result(self, result):
        return try_get_url(
            f'.change_{self.blueprint_name}',
            **{'model_name': self.model_name, 'pk': result.id}
        )

    def items_for_result(self, result):
        """Заполнение строки таблицы"""

        def link_in_col(is_first, field_name):
            if g.fields_link is None:
                return False
            if is_first and not g.fields_link:
                return True
            return field_name in g.fields_link

        first = True
        empty_value_display = self.empty_value_display
        for field_name in g.fields_display:
            row_classes = ["field-%s" % field_name]
            try:
                f, attr, value = lookup_field(field_name, result)
            except (AttributeError, ValueError):
                result_repr = empty_value_display
            else:
                if f is None:
                    boolean = getattr(attr, "boolean", False)
                    result_repr = display_for_value(
                        value, empty_value_display, boolean
                    )
                    if isinstance(value, (datetime.date, datetime.time)):
                        row_classes.append("nowrap")
                else:
                    if isinstance(f.property, Relationship):
                        field_val = getattr(result, field_name)
                        if field_val is None:
                            result_repr = empty_value_display
                        else:
                            result_repr = field_val
                    else:
                        result_repr = display_for_field(
                            value, f.type, empty_value_display
                        )
            row_class = ' class="%s"' % " ".join(row_classes)

            if link_in_col(first, field_name):
                table_tag = "th" if first else "td"
                first = False

                try:
                    url = self.get_url_for_result(result)
                except BuildError:
                    link_or_text = result_repr
                else:
                    link_class = ''
                    if not result_repr:
                        link_class = "empty"
                        label = label_for_field(field_name)
                        result_repr = f'{label} отсутствует'

                    link_or_text = format_html(
                        '<a href="{}"{}>{}</a>',
                        url,
                        format_html(' class="{}"', link_class)
                        if link_class
                        else '',
                        result_repr,
                    )

                yield format_html(
                    "<{}{}>{}</{}>",
                    table_tag,
                    row_class,
                    link_or_text,
                    table_tag
                )
            else:
                yield format_html('<td{}>{}</td>', row_class, result_repr)


class FormMixin(SiteMixin):
    template: str = 'form_result.html'
    methods = ["GET", "POST"]

    def g_init(self):
        super().g_init()
        g.object = self.get_object()

    def get_btn(self):
        return {'btn_save': True, 'btn_save_and_continue': True}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        try:
            context['title'] = g.model.Meta.verbose_name
        except AttributeError:
            pass

        return context

    def get_media(self):
        media = super().get_media()
        if self.model_name == 'si':
            media += Media(js=['js/ajax.js'])

        return media

    def get_form_kwargs(self):
        kwargs = {
            'meta': {'locales': [settings.LANGUAGE]},
            'obj': g.object,
        }
        return kwargs

    def get_form(self):
        form = get_form_class()(**self.get_form_kwargs())
        g.form = form

        return form

    def get_object(self, related_model=None):
        try:
            return Repository.task_get_object(
                filters=self.pk,
                related_model=related_model,
            )
        except NoResultFound:
            abort(404)

    def get_success_url(self):
        return try_get_url(
            f'.list_{self.blueprint_name}', model_name=self.model_name
        )

    def get_success_continue_url(self):
        return request.url

    def pre_save(self, obj):
        for field_name, file in request.files.items():
            field = getattr(g.form, field_name)
            folder = str(os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                field.upload
            ))
            if f'{field_name}_clear' in request.form:
                old_filename = getattr(obj, field_name)
                os.remove(os.path.join(folder, old_filename))
                setattr(obj, field_name, None)
            elif file.filename:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                filename = secure_filename(file.filename)
                old_filename = getattr(obj, field_name)
                if filename == old_filename:
                    continue
                if old_filename:
                    os.remove(os.path.join(folder, old_filename))
                file.save(os.path.join(folder, filename))
                setattr(obj, field_name, filename)
        return obj

    def object_save(self, obj):
        Repository.task_update_object(obj)

    def post(self, **kwargs):
        form = self.get_form()
        if form.validate_on_submit():
            obj = form.instance
            obj = self.pre_save(obj)
            self.object_save(obj)

            if "_continue" in request.form:
                return redirect(self.get_success_continue_url())
            return redirect(self.get_success_url())

        else:
            kwargs['form'] = form
            return self.get(**kwargs)


class ChangeMixin(FormMixin):
    pass


class AddMixin(FormMixin):
    def get_object(self, related_model=None):
        return g.model()

    def get_success_continue_url(self):
        return try_get_url(
            f'.change_{self.blueprint_name}',
            model_name=self.model_name,
            pk=g.object_id
        )

    def object_save(self, obj):
        Repository.task_add_object(obj)


class DeleteMixin(SiteMixin):
    pass
