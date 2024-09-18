from src.core import LOOKUP_SEP, try_get_url
from src.service.views import ListSiView, ChangeSiView


class ListObjectView(ListSiView):
    decorators = []
    fields_filter = [
        'group_si',
        'name_si',
        'type_si',
        'service_type',
        'service_interval',
        'place',
        'control_vp',
        # 'room_delivery',
        'employee',
        'employee' + LOOKUP_SEP + 'division',
        'service' + LOOKUP_SEP + 'date_last_service',
        'service' + LOOKUP_SEP + 'date_next_service',
        'is_service',
    ]
    fields_search = [
        'group_si' + LOOKUP_SEP + 'name',
        'name_si' + LOOKUP_SEP + 'name',
        'type_si' + LOOKUP_SEP + 'name',
        'number',
        'employee' + LOOKUP_SEP + 'last_name',
        'employee' + LOOKUP_SEP + 'first_name',
        'employee' + LOOKUP_SEP + 'middle_name',
    ]

    def get_fields_display(self):
        return [
            'group_si',
            'name_si',
            'type_si',
            'number',
            'description',
            'method',
            'service_type',
            'service_interval',
            'place',
            'control_vp',
            # 'room_delivery',
            'employee',
            'division',
            'email',
            'date_last_service',
            'date_next_service',
            'certificate',
            'status_service',
        ]

    def get_reset_filter_url(self):
        return try_get_url('.index')

    def get_url_for_result(self, result):
        return try_get_url('.view_device', pk=result.id)


class ViewSiView(ChangeSiView):
    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update(readonly=True)

        return kwargs

    def get_history_url(self):
        return try_get_url('.history_device', pk=self.pk)

