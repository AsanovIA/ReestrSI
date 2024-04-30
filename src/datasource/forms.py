from wtforms import StringField, FileField, EmailField
from wtforms.validators import Length, Email, InputRequired, Optional

from src.core import SiteForm, ExtendedSelectField, Unique


class FieldNameForm(SiteForm):
    name = StringField(
        validators=[InputRequired(), Length(max=256), Unique()],
        description='максимум 256 символов'
    )


class GroupSiForm(FieldNameForm):
    """Группы СИ по областям и разделам областей измерений"""


class NameSiForm(FieldNameForm):
    """Наименование СИ"""


class TypeSiForm(FieldNameForm):
    """Тип СИ"""


class DescriptionMethodForm(FieldNameForm):
    """Описание и методика поверки СИ"""

    description = FileField()
    method = FileField()


class ServiceTypeForm(FieldNameForm):
    """Вид метрологического обслуживания"""


class ServiceIntervalForm(FieldNameForm):
    """Межповерочный интервал"""


class PlaceForm(FieldNameForm):
    """Место поверки/калибровки"""


class RoomForm(FieldNameForm):
    """№ помещения где можно получить СИ после поверки (калибровки)"""


class DivisionForm(FieldNameForm):
    """Подразделение"""


class EmployeeForm(SiteForm):
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
    division = ExtendedSelectField(coerce=int, model='Division')
