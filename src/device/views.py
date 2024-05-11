from src.core import try_get_url
from src.service.views import ListSiView


class ListObjectView(ListSiView):
    fields_link = None
    decorators = []

    def get_fields_display(self):
        fields_display = [
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
            'room_delivery',
            'employee',
            'division',
            'email',
            'date_last_service',
            'date_next_service',
            'certificate',
            'is_service',
        ]
        return fields_display

    def get_reset_filter_url(self):
        return try_get_url(f'.index')
