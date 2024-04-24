from wtforms import (
    StringField, FileField, EmailField, SelectField, DateField, IntegerField,
    BooleanField
)
from wtforms.validators import (
    Length, Email, InputRequired, Optional, DataRequired, NumberRange
)

from src.forms import SiteForm
from src.validators import Unique


class FieldNameForm(SiteForm):
    name = StringField(
        label='Наименование',
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

    description = FileField(label='Описание СИ')
    method = FileField(label='Методика поверки СИ')


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
        label='Фамилия',
        validators=[InputRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    first_name = StringField(
        label='Имя',
        validators=[InputRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    middle_name = StringField(
        label='Отчество',
        validators=[InputRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    email = EmailField(
        label='e-mail',
        validators=[
            Optional(),
            Email(),
            Unique(message='Сотрудник с таким e-mail уже существует')
        ]
    )
    division = SelectField(
        label='Подразделение',
        coerce=int,
        render_kw={'model': 'Division'},
    )


class SiForm(SiteForm):
    """Средство измерения"""

    group_si = SelectField(
        label='Группы СИ по областям и разделам областей измерений',
        coerce=int,
        render_kw={'model': 'GroupSi'},
        validators=[DataRequired()],
    )
    name_si = SelectField(
        label='Наименование СИ',
        coerce=int,
        render_kw={'model': 'NameSi'},
        validators=[DataRequired()],
    )
    type_si = SelectField(
        label='Тип СИ',
        coerce=int, render_kw={'model': 'TypeSi'},
    )
    number = StringField(
        label='Заводской номер',
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    description_method = SelectField(
        label='Описание и методика поверки СИ',
        coerce=int,
        render_kw={'model': 'DescriptionMethod'},
    )
    service_type = SelectField(
        label='Вид метрологического обслуживания',
        coerce=int,
        render_kw={'model': 'ServiceType'},
    )
    service_interval = SelectField(
        label='Межповерочный интервал',
        coerce=int,
        render_kw={'model': 'ServiceInterval'},
    )
    etalon = BooleanField(
        label='Эталон',
        default=False
    )
    category_etalon = StringField(
        label='Категория эталона',
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    year_production = IntegerField(
        label='год производства',
        validators=[NumberRange(min=1900, max=2200)],
        description='диапазон от 1900 до 2200',
    )
    nomenclature = StringField(
        label='Номенклатурный номер',
        validators=[Length(max=100)],
        description='максимум 100 символов'
    )
    room_use_etalon = SelectField(
        label='№ помещения, в котором применяется эталон',
        coerce=int,
        render_kw={'model': 'Room'},
    )
    place = SelectField(
        label='Место поверки/калибровки',
        coerce=int,
        render_kw={'model': 'Place'},
    )
    control_vp = BooleanField(
        label='Контроль ВП',
        default=False
    )
    room_delivery = SelectField(
        label='№ помещения где можно получить СИ после поверки',
        coerce=int,
        render_kw={'model': 'Room'},
    )
    employee = SelectField(
        label='Ответственное лицо',
        coerce=int,
        render_kw={'model': 'Employee'},
    )
    date_last_service = DateField(
        label='Дата последней поверки',
        validators=[DataRequired()]
    )
    date_next_service = DateField(
        label='Дата следующей поверки',
        validators=[DataRequired()]
    )
    certificate = FileField(label='Сертификат')
    is_service = BooleanField(
        label='на обслуживании',
        default=False
    )
