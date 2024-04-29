from wtforms import (SelectField, DateField, IntegerField, StringField,
                     BooleanField, TextAreaField, FileField)
from wtforms.validators import Length, NumberRange, Optional, DataRequired

from src.core.forms import SiteForm


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
    )
    type_si = SelectField(
        label='Тип СИ',
        coerce=int,
        render_kw={'model': 'TypeSi'},
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
    etalon = BooleanField(label='Эталон', default=False)
    category_etalon = StringField(
        label='Категория эталона',
        validators=[Length(max=100)],
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
    control_vp = BooleanField(label='Контроль ВП', default=False)
    room_delivery = SelectField(
        label='№ помещения где можно получить СИ после обслуживания',
        coerce=int,
        render_kw={'model': 'Room'},
    )
    employee = SelectField(
        label='Ответственное лицо',
        coerce=int,
        render_kw={'model': 'Employee'},
    )
    division = StringField(
        label='Подразделение',
        render_kw={'readonly': True},
    )
    date_last_service = DateField(
        label='Дата последнего обслуживания',
    )
    date_next_service = DateField(
        label='Дата следующего обслуживания',
    )
    certificate = FileField(label='Сертификат')
    is_service = BooleanField(
        label='на обслуживании',
        default=False,
        render_kw={'readonly': True},
    )


class ServiceForm(SiteForm):
    """Обслуживание СИ"""

    date_in_service = DateField(
        label='Дата поступления на обслуживание',
        render_kw={'readonly': True},
    )
    date_out_service = DateField(
        label='Дата возврата с обслуживания',
        validators=[Optional()]
    )
    date_last_service = DateField(
        label='Дата последнего обслуживания',
        validators=[Optional()],
        render_kw={'readonly': True},
    )
    date_next_service = DateField(
        label='Дата следующего обслуживания',
        validators=[Optional()]
    )
    is_ready = BooleanField(label='готов к выдачи', default=False)
    certificate = FileField(label='Сертификат')
    note = TextAreaField(
        label='Примечание',
        validators=[Length(max=1000)],
        description='максимум 1000 символов'
    )


class AddServiceForm(SiteForm):
    """Добавление СИ на обслуживание"""

    date_in_service = DateField(
        label='Дата поступления на обслуживание',
        validators=[DataRequired()]
    )


class OutServiceForm(SiteForm):
    """Выдача СИ с обслуживания"""

    date_out_service = DateField(
        label='Дата возврата с обслуживания',
    )
    date_next_service = DateField(
        label='Дата следующего обслуживания',
    )
    certificate = FileField(label='Сертификат')
    note = TextAreaField(
        label='Примечание',
        validators=[Length(max=1000)],
        description='максимум 1000 символов'
    )
