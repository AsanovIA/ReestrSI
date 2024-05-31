import os

from flask import g
from sqlalchemy.exc import NoResultFound

from src.core import Media, Query
from src.db.repository import Repository
from src.core.mixins import ListMixin, ChangeMixin, AddMixin, DeleteMixin
from src.core.utils import get_model, try_get_url, format_html


class SiMixin:
    model_name = 'si'

    def get_success_url(self):
        return try_get_url('.list_si')


class ServiceMixin:
    model_name = 'service'

    def get_success_url(self):
        return try_get_url(f'.list_service')

    def object_save(self, obj):
        obj = [obj, g.object_si]
        Repository.task_add_or_update_object(obj)


class ListSiView(SiMixin, ListMixin):
    sidebar = 'filter_sidebar'

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

    def get_delete_url(self):
        return try_get_url(
            f'.delete_{self.blueprint_name}',
            pk=g.object.id
        )

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

        context['delete_url'] = self.get_delete_url()
        context['btn']['btn_delete'] = True

        return context

    def get_media(self):
        media = super().get_media()
        media += Media(js=['js/ajax.js'])

        return media


class AddSiView(SiMixin, AddMixin):
    def get_media(self):
        media = super().get_media()
        media += Media(js=['js/ajax.js'])

        return media


class DeleteSiView(SiMixin, DeleteMixin):

    def get_deleted_objects(self):
        model = get_model('service')
        query = Query(model=model, filters=[model.si_id == self.pk])
        history_list = Repository.task_get_list(query)
        list_files = []
        field = model.certificate
        for obj in history_list:
            filename = getattr(obj, field.name)
            if not filename:
                continue
            path_file = str(os.path.join(field.info['upload'], filename))
            link_file = format_html(
                '<a href="{}" target="_blank">{}</a>',
                try_get_url('source.view_file', filename=path_file),
                filename
            )
            list_files.append(link_file)

        return list_files

    def get_object_url(self, obj):
        return try_get_url(
            f'.change_{self.blueprint_name}',
            pk=obj.id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deleted_objects'] = self.get_deleted_objects()

        return context

    def post(self, **kwargs):
        model = get_model('service')
        query = Query(model=model, filters=[model.si_id == self.pk])
        history_list = Repository.task_get_list(query)
        for obj in history_list:
            self.delete_files(model.__table__.columns, obj)

        return super().post(**kwargs)


class ListServiceView(ListMixin):
    model_name = 'service'
    sidebar = 'filter_sidebar'

    def get_btn(self):
        return {}

    def get_url_for_result(self, result):
        return try_get_url(f'.change_{self.blueprint_name}', pk=result.id)

    def get_query(self, query):
        query = super().get_query(query)
        query += Query(filters=[g.model.is_out == False])
        return query

    def get_count_list(self):
        return Query(filters=[g.model.is_out == False])


class ChangeServiceView(ServiceMixin, ChangeMixin):

    def get_btn(self):
        btn = super().get_btn()
        btn.update(btn_history=True, btn_service=True)
        return btn

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        si = g.object.si
        context['history_url'] = try_get_url(
            '.history_service', pk=si.id
        )
        context['service_url'] = try_get_url('.out_service', pk=self.pk)
        context['link_text'] = 'Выдать СИ'
        context['content_title'] = f'обслуживание средства измерения: {str(si)}'

        return context

    def pre_save(self, obj):
        g.object_si = obj.si
        g.object_si.status_service_id = obj.status_service_id

        return obj


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

    def get_object_url(self, obj):
        return try_get_url(
            f'admin.si.change_si',
            pk=obj.id
        )

    def pre_save(self, obj):
        si = g.object_si

        obj.is_out = True

        si.is_service = False
        si.status_service_id = None
        si.date_last_service = obj.date_last_service
        si.date_next_service = obj.date_next_service
        si.certificate = obj.certificate

        return obj

    def get_success_message(self, obj):
        obj = g.object_si
        name_str = str(obj)
        obj_url = self.get_object_url(obj)
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


class AddServiceView(ServiceMixin, AddMixin):
    form_class_name = 'AddServiceForm'

    def g_init(self):
        super().g_init()
        g.object_si = Repository.task_get_object(self.pk, get_model('si'))

    def get_btn(self):
        return {'btn_change': True, 'btn_text': 'Направить на обслуживание'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_title'] = f'Прием на обслуживание: {str(g.object_si)}'

        return context

    def get_object_url(self, obj):
        return try_get_url(
            f'admin.si.change_si',
            pk=obj.id
        )

    def get_success_url(self):
        return try_get_url(f'.list_si')

    def pre_save(self, obj):
        si = g.object_si
        si.is_service = True
        si.status_service_id = obj.status_service_id

        obj.si_id = si.id
        obj.date_last_service = si.date_next_service

        return obj

    def get_success_message(self, obj):
        obj = g.object_si
        name_str = str(obj)
        obj_url = self.get_object_url(obj)
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


class HistoryServiceView(ListMixin):
    model_name = 'service'
    fields_link = None

    def get_fields_display(self):
        model = get_model('service')
        return model.Meta.fields_display

    def get_btn(self):
        return {}

    def get_query(self, query):
        query = super().get_query(query)
        query += Query(filters=[g.model.si_id == self.pk])
        return query

    def get_count_list(self):
        return Query(filters=[g.model.si_id == self.pk])
