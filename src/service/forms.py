from wtforms import (DateField, IntegerField, StringField, BooleanField,
                     TextAreaField, FileField)
from wtforms.validators import Length, NumberRange, Optional, DataRequired

from src.core import SiteForm, ExtendedSelectField


class SiForm(SiteForm):
    """Средство измерения"""

    group_si = ExtendedSelectField(
        label='Группы СИ по областям и разделам областей измерений',
        coerce=int,
        model='GroupSi',
        validators=[DataRequired()],
    )
    name_si = ExtendedSelectField(
        label='Наименование СИ',
        coerce=int,
        model='NameSi',
    )
    type_si = ExtendedSelectField(
        label='Тип СИ',
        coerce=int,
        model='TypeSi',
    )
    number = StringField(
        label='Заводской номер',
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    description_method = ExtendedSelectField(
        label='Описание и методика поверки СИ',
        coerce=int,
        model='DescriptionMethod',
    )
    service_type = ExtendedSelectField(
        label='Вид метрологического обслуживания',
        coerce=int,
        model='ServiceType',
    )
    service_interval = ExtendedSelectField(
        label='Межповерочный интервал',
        coerce=int,
        model='ServiceInterval',
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
    room_use_etalon = ExtendedSelectField(
        label='№ помещения, в котором применяется эталон',
        coerce=int,
        model='Room',
    )
    place = ExtendedSelectField(
        label='Место поверки/калибровки',
        coerce=int,
        model='Place',
    )
    control_vp = BooleanField(label='Контроль ВП', default=False)
    room_delivery = ExtendedSelectField(
        label='№ помещения где можно получить СИ после обслуживания',
        coerce=int,
        model='Room',
    )
    employee = ExtendedSelectField(
        label='Ответственное лицо',
        coerce=int,
        model='Employee',
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
