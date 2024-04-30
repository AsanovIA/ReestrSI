from flask import g
from sqlalchemy.exc import NoResultFound

from src.db.repository import Repository
from src.core.mixins import ListMixin, ChangeMixin, AddMixin
from src.core.utils import get_model, try_get_url
from src.service.models import *


class SiMixin:
    model_name = 'si'

    def get_success_url(self):
        return try_get_url('.list_si')


class ServiceMixin:
    model_name = 'service'

    def get_success_url(self):
        return try_get_url(f'.list_service')


class ListSiView(ListMixin):
    model_name = 'si'

    def get_query(self, **kwargs):
        kwargs = super().get_query(**kwargs)
        kwargs['model_related'] = {'employee': get_model('employee')}
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        division = getattr(g.object.employee, 'division', None)
        if division:
            kwargs['division'] = g.object.employee.division
        else:
            kwargs['division'] = self.empty_value_display

        return kwargs

    def get_object(self, model_related=None):
        model_related = {'employee': get_model('employee')}
        return super().get_object(model_related)


class AddSiView(SiMixin, AddMixin):
    pass


class ListServiceView(ListMixin):
    model_name = 'service'

    def get_btn(self):
        return {}

    def get_url_for_result(self, result):
        return try_get_url(f'.change_{self.blueprint_name}', pk=result.id)

    def get_query(self, **kwargs):
        kwargs = super().get_query(**kwargs)
        filters = [
            g.model.is_out == False,
        ]
        kwargs.update(filters=filters)
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

    def get_btn(self):
        return {'btn_change': True, 'btn_text': 'Выдать'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        si = g.object.si
        context['content_title'] = f'Выдача с обслуживания: {str(si)}'

        return context

    def pre_save(self, obj):
        obj.is_out = True

        si = obj.si
        si.is_service = False
        si.date_last_service = obj.date_last_service
        si.date_next_service = obj.date_next_service
        si.certificate = obj.certificate

        return [obj, si]

    def object_save(self, obj):
        Repository.task_add_or_update_object(obj)


class AddServiceView(ServiceMixin, AddMixin):
    form_class_name = 'AddServiceForm'

    def get_btn(self):
        return {'btn_change': True, 'btn_text': 'Направить на обслуживание'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        si = Repository.task_get_object(self.pk, model=get_model('si'))
        context['content_title'] = f'Прием на обслуживание: {str(si)}'

        return context

    def get_success_url(self):
        return try_get_url(f'.list_si')

    def pre_save(self, obj):
        si = Repository.task_get_object(self.pk, model=get_model('si'))
        si.is_service = True

        obj.si_id = si.id
        obj.date_last_service = si.date_next_service

        return [obj, si]

    def object_save(self, obj):
        Repository.task_add_or_update_object(obj)


class HistoryServiceView(ListMixin):
    model_name = 'service'
    fields_link = None

    def get_btn(self):
        return {}

    def get_query(self, **kwargs):
        kwargs = super().get_query(**kwargs)
        filters = [
            g.model.si_id == self.pk,
        ]
        kwargs.update(filters=filters)
        return kwargs
