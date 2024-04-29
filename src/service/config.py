from src.service.models import (
    Si,
    Service
)

app_settings = {
    'name': 'service',
    'verbose_name': 'Обслуживание СИ',
    'models': {
        'Si'.lower(): Si,
        'Service'.lower(): Service,
    }
}
