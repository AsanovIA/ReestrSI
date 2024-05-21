from wtforms import StringField, EmailField, BooleanField
from wtforms.validators import Length, Email, InputRequired, Optional

from src.core import SiteForm, ExtendedFileField, ExtendedSelectField, Unique


class FieldViewForm(SiteForm):
    view = BooleanField(
        default=True,
        description=("Отметьте, если значение должно отображаться в списке "
                     "выбора. Уберите эту отметку вместо удаления значения.")
    )


class FieldViewNameForm(FieldViewForm):
    name = StringField(
        validators=[InputRequired(), Length(max=256), Unique()],
        description='максимум 256 символов'
    )

    class Meta:
        fields = ['name', 'view']


class GroupSiForm(FieldViewNameForm):
    """Группы СИ по областям и разделам областей измерений"""


class NameSiForm(FieldViewNameForm):
    """Наименование СИ"""


class TypeSiForm(FieldViewNameForm):
    """Тип СИ"""


class DescriptionMethodForm(FieldViewNameForm):
    """Описание и методика поверки СИ"""

    description = ExtendedFileField()
    method = ExtendedFileField()

    class Meta:
        fields = ['name', 'description', 'method', 'view']


class ServiceTypeForm(FieldViewNameForm):
    """Вид метрологического обслуживания"""


class ServiceIntervalForm(FieldViewNameForm):
    """Межповерочный интервал"""


class PlaceForm(FieldViewNameForm):
    """Место поверки/калибровки"""


class RoomForm(FieldViewNameForm):
    """№ помещения где можно получить СИ после поверки (калибровки)"""


class StatusServiceForm(FieldViewNameForm):
    """Состояние обслуживания СИ"""


class DivisionForm(FieldViewNameForm):
    """Подразделение"""


class EmployeeForm(FieldViewForm):
    """Ответственное лицо (сотрудник)"""

    last_name = StringField(
        validators=[InputRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    first_name = StringField(
        validators=[InputRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    middle_name = StringField(
        validators=[InputRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    email = EmailField(
        validators=[
            Optional(),
            Email(),
            Unique(message='Сотрудник с таким e-mail уже существует')
        ]
    )
    division = ExtendedSelectField(model='Division')

    class Meta:
        fields = (
            'last_name', 'first_name', 'middle_name', 'email', 'division',
            'view'
        )
