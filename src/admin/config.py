from src.admin.models import (
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
    Si,
)

app_settings = {
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
    'Si'.lower(): Si,
}