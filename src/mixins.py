import datetime
from typing import Union

from flask import abort, g, request, render_template
from flask.views import View
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Relationship
from werkzeug.routing import BuildError
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import FileField, MultipleFileField

from src.db.repository import Repository
from src.utils import (
    FIELDS_EXCLUDE,
    display_for_field,
    display_for_value,
    format_html,
    get_form_class,
    get_model,
    label_for_field,
    lookup_field,
    try_get_url,
)


class SiteMixin(View):
    template = None
    model_name = None
    pk = None
    model = None
    form_class_name = None
    empty_value_display = '-'

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

    def get_context_data(self, **kwargs):
        context = {
            'title': 'Средства измерения',
            'perm': {'perm_change': False},
        }
        if 'admin' in request.blueprints:
            context.update({
                'main_menu': self.get_admin_main_menu(),
                'perm': {
                    'perm_add': True, 'perm_delete': True, 'perm_change': True,
                },
            })
        kwargs.update(context)

        return kwargs

    @classmethod
    def get_admin_main_menu(cls):
        main_menu = [
            {
                'title': 'Главная',
                'url': try_get_url('')
            },
            {
                'title': 'Обслуживание',
                'url': try_get_url('')
            },
            {
                'title': 'Настройки',
                'url': try_get_url('')
            },
        ]
        return main_menu


class ListMixin(SiteMixin):
    template: str = 'list_result.html'
    fields_display: Union[list[str], tuple[str]] = ()
    fields_link: Union[list[str], tuple[str], None] = ()

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result_list = Repository.task_get_list(**kwargs)
        context['result_headers'] = list(self.get_result_headers())
        context['results'] = list(self.get_results(result_list))

        return context

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
            except AttributeError:
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
    
    def g_init(self):
        super().g_init()
        g.object = self.get_object()    

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()

        return context

    def get_form(self):
        form = get_form_class()(obj=g.object)
        instance = getattr(g, 'object', None)
        g.form = form
        form.fields = []
        for field in form:
            if field.name not in FIELDS_EXCLUDE:
                form.fields.append(field.name)
            label_class = {}
            if getattr(field.flags, 'required', None):
                label_class = {'class': 'required'}
            field.label_class = label_class
            if isinstance(field, (FileField, MultipleFileField)):
                form.is_multipart = True
            if isinstance(field, SelectField):
                model_name = field.render_kw.pop('model')
                if model_name is None:
                    raise TypeError(
                        f'Отсутствует ключ "model" параметра "render_kw" для '
                        f'{field.name} класса {form.__class__.__name__}'
                    )
                model_related = get_model(model_name)
                kwargs = {'model': model_related}
                choices = [
                    (obj.id, obj)
                    for obj in Repository.task_get_list(**kwargs)
                ]
                setattr(field, 'choices', choices)

                value = form.data[field.name]
                if value is None:
                    value = getattr(instance, f'{field.name}_id', None)
                setattr(field, 'data', value)

        return form

    def get_object(self):
        raise NotImplementedError(
            f"не определен метод get_object() для {self.__class__.__name__}"
        )


class ChangeMixin(FormMixin):
    def get_object(self):
        try:
            return  Repository.task_get_object(filters=self.pk)
        except NoResultFound:
            abort(404)


class AddMixin(FormMixin):
    def get_object(self):
        return None


class DeleteMixin(SiteMixin):
    pass
