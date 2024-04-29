from src.datasource.models import (
    GroupSi,
    NameSi,
    TypeSi,
    ServiceType,
    ServiceInterval,
    DescriptionMethod,
    Place,
    Room,
    Division,
    Employee,
)

app_settings = {
    'name': 'datasource',
    'verbose_name': 'База зависимостей',
    'models': {
        'GroupSi'.lower(): GroupSi,
        'NameSi'.lower(): NameSi,
        'TypeSi'.lower(): TypeSi,
        'ServiceType'.lower(): ServiceType,
        'ServiceInterval'.lower(): ServiceInterval,
        'DescriptionMethod'.lower(): DescriptionMethod,
        'Place'.lower(): Place,
        'Room'.lower(): Room,
        'Division'.lower(): Division,
        'Employee'.lower(): Employee,
    }
}
