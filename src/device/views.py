from src.core import LOOKUP_SEP, try_get_url, SiteMixin
from src.service.views import ListSiView, ChangeSiView, HistoryServiceView


class UserSiView(SiteMixin):
    fields = [
        'name_si',
        'type_si',
        'number',
        'description',
        'method',
        'service_type',
        'service_interval',
        'place',
        'control_vp',
        'employee',
        'division',
        'status_service',
        'date_last_service',
        'certificate',
        'date_next_service',
    ]

    def get_main_menu(self, endpoint=None):
        return super().get_main_menu('.index')


class UserListSiView(UserSiView, ListSiView):
    decorators = []
    fields_filter = [
        'name_si',
        'type_si',
        'service_type',
        'service_interval',
        'place',
        'control_vp',
        'employee',
        'employee' + LOOKUP_SEP + 'division',
        'is_service',
        'service' + LOOKUP_SEP + 'date_last_service',
        'service' + LOOKUP_SEP + 'date_next_service',
    ]
    fields_search = [
        'name_si' + LOOKUP_SEP + 'name',
        'type_si' + LOOKUP_SEP + 'name',
        'number',
        'employee' + LOOKUP_SEP + 'last_name',
        'employee' + LOOKUP_SEP + 'first_name',
        'employee' + LOOKUP_SEP + 'middle_name',
    ]

    def get_fields_display(self):
        return self.fields

    def get_reset_filter_url(self):
        return try_get_url('.index')

    def get_url_for_result(self, result):
        return try_get_url('.view_device', pk=result.id)


class UserObjectSiView(UserSiView, ChangeSiView):

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs['fields'] = self.fields
        kwargs['readonly_fields'] = self.fields

        return kwargs

    def get_history_url(self):
        return try_get_url('.history_device', pk=self.pk)


class UserHistoryServiceView(UserSiView, HistoryServiceView):
    pass
