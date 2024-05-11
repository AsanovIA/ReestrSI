from flask import g
from sqlalchemy.exc import NoResultFound

from src.db.repository import Repository
from src.core.mixins import ListMixin, ChangeMixin, AddMixin
from src.core.utils import get_model, try_get_url, format_html
from src.service.models import *


class SiMixin:
    model_name = 'si'

    def get_model_related(self):
        return {
            'employee': get_model('employee'),
        }

    def get_success_url(self):
        return try_get_url('.list_si')


class ServiceMixin:
    model_name = 'service'

    def get_model_related(self):
        return {
            'employee': get_model('employee'),
        }

    def get_success_url(self):
        return try_get_url(f'.list_service')


class ListSiView(SiMixin, ListMixin):
    sidebar = 'filter_sidebar'

    def get_query(self, **kwargs):
        kwargs = super().get_query(**kwargs)
        kwargs.setdefault('model_related', self.get_model_related())

        return kwargs

    def get_add_url(self):
        return try_get_url('.add_si')

    def get_url_for_result(self, result):
        return try_get_url('.change_si', pk=result.id)


class ChangeSiView(SiMixin, ChangeMixin):

    def get_btn(self):
        btn = super().get_btn()
        btn.update({'btn_history': True, 'btn_service': True})
        return btn

    def get_service_url(self):
        try:
            service = Repository.task_get_object(
                filters={'si_id': g.object.id, 'is_out': False},
                model=get_model('service')
            )
        except NoResultFound:
            return ''

        return try_get_url(f'admin.service.change_service', pk=service.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history_url'] = try_get_url(
            'admin.service.history_service', pk=self.pk
        )
        if g.object.is_service:
            context['service_url'] = self.get_service_url()
            context['link_text'] = 'Посмотреть в обслуживании'
        else:
            context['service_url'] = try_get_url('.add_service', pk=self.pk)
            context['link_text'] = 'Направить на обслуживание'

        return context

    def get_object(self, model_related=None):
        model_related = self.get_model_related()
        return super().get_object(model_related)


class AddSiView(SiMixin, AddMixin):
    pass


class ListServiceView(ListMixin):
    model_name = 'service'
    sidebar = 'filter_sidebar'

    def get_btn(self):
        return {}

    def get_url_for_result(self, result):
        return try_get_url(f'.change_{self.blueprint_name}', pk=result.id)

    def get_query(self, **kwargs):
        kwargs = super().get_query(**kwargs)
        filters = kwargs.get('filters', [])
        filters.append(g.model.is_out == False)
        kwargs['filters'] = filters

        return kwargs


class ChangeServiceView(ServiceMixin, ChangeMixin):

    def get_btn(self):
        btn = super().get_btn()
        btn.update(btn_history=True, btn_service=True)
        return btn

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history_url'] = try_get_url(
            '.history_service', pk=g.object.si_id
        )
        if g.object.is_ready:
            context['service_url'] = try_get_url('.out_service', pk=self.pk)
            context['link_text'] = 'Выдать СИ'
        else:
            context['service_url'] = ''
            context['link_text'] = 'СИ не готово к выдачи'
            context['class_link'] = 'deletelink'
        si = g.object.si
        context['content_title'] = f'обслуживание средства измерения: {str(si)}'

        return context


class OutServiceView(ServiceMixin, ChangeMixin):
    form_class_name = 'OutServiceForm'

    def g_init(self):
        super().g_init()
        g.object_si = g.object.si

    def get_btn(self):
        return {'btn_change': True, 'btn_text': 'Выдать'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_title'] = f'Выдача с обслуживания: {str(g.object.si)}'

        return context

    def get_object_url(self):
        return try_get_url(
            f'admin.si.change_si',
            pk=g.object_si.id
        )

    def pre_save(self, obj):
        obj.is_out = True

        si = g.object_si
        si.is_service = False
        si.date_last_service = obj.date_last_service
        si.date_next_service = obj.date_next_service
        si.certificate = obj.certificate

        return [obj, si]

    def get_success_message(self):
        obj = g.object_si
        name_str = str(obj)
        obj_url = self.get_object_url()
        link_or_text = format_html(
            '<a href="{}">{}</a>', obj_url, name_str
        )
        message = format_html(
            '{} "{}" завершил{} обслуживание.',
            obj.Meta.verbose_name,
            link_or_text,
            obj.Meta.action_suffix,
        )

        return message

    def object_save(self, obj):
        Repository.task_add_or_update_object(obj)


class AddServiceView(ServiceMixin, AddMixin):
    form_class_name = 'AddServiceForm'

    def g_init(self):
        super().g_init()
        g.object_si = self.get_si()

    def get_btn(self):
        return {'btn_change': True, 'btn_text': 'Направить на обслуживание'}

    def get_si(self):
        return Repository.task_get_object(
            self.pk, get_model('si'), self.get_model_related()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_title'] = f'Прием на обслуживание: {str(g.object_si)}'

        return context

    def get_object_url(self):
        return try_get_url(
            f'admin.si.change_si',
            pk=g.object_si.id
        )

    def get_success_url(self):
        return try_get_url(f'.list_si')

    def pre_save(self, obj):
        si = g.object_si
        si.is_service = True

        obj.si_id = si.id
        obj.date_last_service = si.date_next_service

        return [obj, si]

    def get_success_message(self):
        obj = g.object_si
        name_str = str(obj)
        obj_url = self.get_object_url()
        link_or_text = format_html(
            '<a href="{}">{}</a>', obj_url, name_str
        )
        message = format_html(
            '{} "{}" добавлен{} в список обслуживаемых.',
            obj.Meta.verbose_name,
            link_or_text,
            obj.Meta.action_suffix,
        )

        return message

    def object_save(self, obj):
        Repository.task_add_or_update_object(obj)


class HistoryServiceView(ListMixin):
    model_name = 'service'
    fields_link = None
    fields_display = [
        'si', 'date_in_service', 'date_last_service', 'is_ready', 'is_out',
        'date_next_service', 'certificate', 'note'
    ]

    def get_btn(self):
        return {}

    def get_query(self, **kwargs):
        kwargs = super().get_query(**kwargs)
        filters = kwargs.get('filters', [])
        filters.append(g.model.si_id == self.pk)
        kwargs['filters'] = filters

        return kwargs
