import os
import datetime
from typing import Union, List, Tuple

from flask import (
    abort, current_app, flash, g, redirect, render_template, request
)
from flask.views import View
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Relationship
from werkzeug.routing import BuildError

from src.config import settings
from src.db.repository import Repository
from src.core.constants import (
    EMPTY_VALUE_DISPLAY, LIMIT_PAGE, LOOKUP_SEP, PAGE_VAR, SEARCH_VAR
)
from src.core.filters import FilterForm
from src.core.queries import Query
from src.core.media import Media
from src.core.utils import (
    display_for_field,
    display_for_value,
    format_html,
    get_app_settings,
    get_form_class,
    get_model,
    label_for_field,
    lookup_field,
    secure_filename,
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
    perm_change = False
    perm_add = False
    perm_delete = False

    def __init__(self, blueprint_name, template=None):
        self.blueprint_name = blueprint_name
        if template is not None:
            self.template = template

    @property
    def perm(self):
        return self.perm_add or self.perm_change or self.perm_delete

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
        context = {}
        if 'admin' in request.blueprints:
            self.perm_change = True
            self.perm_add = True
            self.perm_delete = True
            if hasattr(g.model.Meta, 'verbose_name_change'):
                object_verbose_name = g.model.Meta.verbose_name_change
            elif hasattr(g.model.Meta, 'verbose_name'):
                object_verbose_name = g.model.Meta.verbose_name
            else:
                object_verbose_name = ''

            context.update({
                'object_verbose_name': object_verbose_name,
                'username': g.user.get_short_name(),
            })

        context.update({
            'title': settings.SITE_NAME,
            'sidebar': self.sidebar,
            'media': self.get_media(),
            'btn': self.get_btn(),
            'main_menu': self.get_main_menu(),
            'perm': {
                'perm_change': self.perm_change,
                'perm_add': self.perm_add,
                'perm_delete': self.perm_delete,
            },
        })
        kwargs.update(context)

        return kwargs

    def get_media(self):
        media = Media()

        return media

    def get_main_menu(self, endpoint=None):
        main_menu = []
        if endpoint is None:
            endpoint = 'admin.si.list_si'
        main_menu += [
            {
                'title': 'Средства измерения',
                'url': try_get_url(endpoint)
            },
        ]
        if self.perm:
            main_menu += [
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
        from src.core.utils import SETTINGS_APPS

        app_list = []
        settings_app_list = SETTINGS_APPS

        if label:
            settings_app_list = {label: SETTINGS_APPS[label]}

        for app_label, app_modul in settings_app_list.items():
            app_settings = get_app_settings(app_modul)
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
    fields_filter: Union[List[str], Tuple[str], None] = ()
    fields_search: Union[List[str], Tuple[str], None] = ()
    per_page: int = LIMIT_PAGE

    def g_init(self):
        super().g_init()
        fields_display = self.get_fields_display()
        if fields_display:
            g.fields_display = fields_display
        else:
            raise ValueError(
                f'Не указан список полей "fields_display" отображения для '
                f'модели {g.model.__name__}'
            )

        g.fields_link = self.get_attr_fields('fields_link')
        g.fields_filter = self.get_attr_fields('fields_filter')
        g.fields_search = self.get_attr_fields('fields_search')

    def get_fields_display(self):
        return self.fields_display or getattr(
            g.model.Meta, 'fields_display', []
        )

    def get_attr_fields(self, attr_name):
        attr = getattr(self, attr_name)
        if attr is None or attr:
            return attr
        else:
            return getattr(g.model.Meta, attr_name, ())

    def get_btn(self):
        return {'btn_add': True}

    def get_add_url(self):
        return try_get_url(
            f'.add_{self.blueprint_name}', model_name=self.model_name
        )

    def get_reset_filter_url(self):
        return try_get_url(f'.list_{self.blueprint_name}')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = request.args.get(
            get_page_parameter(param=PAGE_VAR), type=int, default=1
        )
        per_page = self.per_page
        offset = (page - 1) * per_page
        query = Query(limit=per_page, offset=offset)
        result_list = self.get_queryset(query)
        context['pagination'] = self.get_paginator(
            **{PAGE_VAR: page, 'per_page': per_page}
        )
        context['result_headers'] = list(self.get_result_headers())
        context['results'] = list(self.get_results(result_list))
        context['add_url'] = self.get_add_url()
        if self.sidebar == 'filter_sidebar' and g.fields_filter:
            context['filters'] = FilterForm()
            context['reset_filter_url'] = self.get_reset_filter_url()

        if g.fields_search:
            params = dict(request.args)
            if PAGE_VAR in params:
                del params[PAGE_VAR]
            context['search'] = {
                'name': SEARCH_VAR,
                'query': request.args.get(SEARCH_VAR) or "",
                'help_text': self.get_search_help_text(),
                'params': params
            }

        try:
            context['title'] = g.model.Meta.verbose_name_plural
        except AttributeError:
            pass

        return context

    def get_search_help_text(self):
        text = 'Поиск по: '
        labels = []
        for field_name in g.fields_search:
            label = label_for_field(field_name.split(LOOKUP_SEP)[0])
            if f'"{label}"' not in labels:
                labels.append(f'"{label}"')
        text += ', '.join(labels)
        return text + '.'

    def get_query(self, query=None):
        if query is None:
            query = Query()
        if not request.args:
            return query
        query += Query(params=request.args, fields_search=g.fields_search)
        return query

    def get_queryset(self, query):
        queryset = Repository.task_get_list(q=self.get_query(query))
        return queryset

    def get_paginator(self, **kwargs) -> Pagination:
        total = Repository.task_count(q=self.get_query())
        return Pagination(
            page_parameter=PAGE_VAR,
            total=total,
            display_msg="показано <b>{start} - {end}</b> записей из"
                        " <b>{total}</b>",
            search_msg='',
            css_framework='bootstrap5',
            **kwargs
        )

    @staticmethod
    def get_result_headers():
        """Создание заголовков столбцов таблицы"""

        for field_name in g.fields_display:
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
                            value, f, empty_value_display
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


class ObjectMixin(SiteMixin):
    methods = ["GET", "POST"]
    action = None

    def g_init(self):
        super().g_init()
        g.object = self.get_object()

    def get_object(self):
        try:
            return Repository.task_get_object(filters=self.pk)
        except NoResultFound:
            abort(404)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['title'] = g.model.Meta.verbose_name
        except AttributeError:
            pass

        return context

    def get_success_url(self):
        return try_get_url(
            f'.list_{self.blueprint_name}', model_name=self.model_name
        )

    def get_object_url(self, obj):
        return try_get_url(
            f'.change_{self.blueprint_name}',
            model_name=self.model_name,
            pk=obj.id
        )

    def get_success_message(self, obj):
        actions = {'add': 'добавлен', 'change': 'изменен', 'delete': 'удален'}
        name_str = str(obj)
        resume_text = ''
        link_or_text = name_str
        if "_continue" in request.form:
            resume_text = ' Можете продолжить редактирование.'
        else:
            if self.action != 'delete':
                obj_url = self.get_object_url(obj)
                link_or_text = format_html(
                    '<a href="{}">{}</a>', obj_url, name_str
                )

        message = format_html(
            '{} "{}" успешно {}{}.{}',
            obj.Meta.verbose_name,
            link_or_text,
            actions[self.action],
            obj.Meta.action_suffix,
            resume_text,
        )

        return message


class FormMixin(ObjectMixin):
    template: str = 'form_result.html'

    def get_btn(self):
        return {
            'btn_save': True, 'btn_save_and_continue': True
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()

        return context

    def get_form_kwargs(self, **kwargs):
        kwargs = {
            'meta': {'locales': settings.LANGUAGES},
            'obj': g.object,
        }
        return kwargs

    def get_form(self):
        form = get_form_class()(**self.get_form_kwargs())
        g.form = form

        return form

    def get_delete_url(self):
        return try_get_url(
            f'.delete_{self.blueprint_name}',
            model_name=self.model_name,
            pk=g.object.id
        )

    def get_success_continue_url(self):
        return request.url

    def pre_save(self, obj):
        return obj

    def object_save(self, obj):
        Repository.task_update_object(obj)

    def change_files(self, obj):
        for field_name, file in request.files.items():
            field_hash = field_name + '_hash'
            field = getattr(g.form, field_name)
            folder = str(os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                field.upload
            ))
            old_filename = getattr(obj, field_name)
            if f'{field_name}_clear' in request.form:
                os.remove(os.path.join(folder, old_filename))
                setattr(obj, field_name, None)
                setattr(obj, field_hash, None)
            elif file.filename:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                if old_filename:
                    os.remove(os.path.join(folder, old_filename))
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder, filename))
                setattr(obj, field_name, filename)
                setattr(obj, field_hash, field.filehash)

        return obj

    def post(self, **kwargs):
        form = self.get_form()
        if form.validate_on_submit():
            if form.has_changed():
                obj = form.instance
                if request.files:
                    obj = self.change_files(obj)
                obj = self.pre_save(obj)
                self.object_save(obj)

                message = self.get_success_message(obj)
                category = 'success'

            else:
                message = 'Изменения отсутствуют. Сохранение отменено.'
                category = 'warning'

            flash(message, category)
            if "_continue" in request.form:
                return redirect(self.get_success_continue_url())
            return redirect(self.get_success_url())

        else:
            flash('Форма заполнена неверно!', 'error')
            kwargs['form'] = form
            return self.get(**kwargs)


class ChangeMixin(FormMixin):
    action = 'change'


class AddMixin(FormMixin):
    action = 'add'

    def get_object(self):
        return

    def get_success_continue_url(self):
        return try_get_url(
            f'.change_{self.blueprint_name}',
            model_name=self.model_name,
            pk=g.object.id
        )

    def object_save(self, obj):
        Repository.task_add_object(obj)


class DeleteMixin(ObjectMixin):
    template: str = 'delete.html'
    action = 'delete'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = g.model.Meta.verbose_name
        try:
            context['object_url'] = format_html(
                '<a href="{}" class ="text">{}</a>',
                self.get_object_url(g.object),
                g.object
            )
        except BuildError:
            context['object_url'] = g.object

        return context

    def delete_files(self, fields, obj):
        for field in fields:
            if (
                    hasattr(field, 'info')
                    and 'type' in field.info
                    and field.info['type'] == 'FileField'
            ):
                filename = getattr(obj, field.name)
                if not filename:
                    continue
                path_file = str(os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    field.info['upload'],
                    filename
                ))
                if os.path.exists(path_file):
                    os.remove(path_file)

    def post(self, **kwargs):
        obj = g.object
        self.delete_files(g.model.__table__.columns, obj)
        Repository.task_delete_object(obj)

        message = self.get_success_message(obj)
        flash(message, category='success')

        return redirect(self.get_success_url())
