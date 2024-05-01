from wtforms import (
    DateField, IntegerField, StringField, BooleanField, TextAreaField
)
from wtforms.validators import Length, NumberRange, Optional, DataRequired

from src.core import SiteForm, ExtendedFileField, ExtendedSelectField


class SiForm(SiteForm):
    """Средство измерения"""

    group_si = ExtendedSelectField(
        coerce=int, model='GroupSi', validators=[DataRequired()]
    )
    name_si = ExtendedSelectField(coerce=int, model='NameSi')
    type_si = ExtendedSelectField(coerce=int, model='TypeSi')
    number = StringField(
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    description_method = ExtendedSelectField(
        coerce=int, model='DescriptionMethod'
    )
    service_type = ExtendedSelectField(coerce=int,model='ServiceType')
    service_interval = ExtendedSelectField(coerce=int, model='ServiceInterval')
    etalon = BooleanField(default=False)
    category_etalon = StringField(
        validators=[Length(max=100)],
        description='максимум 100 символов'
    )
    year_production = IntegerField(
        validators=[NumberRange(min=1900, max=2200), Optional()],
        description='диапазон от 1900 до 2200',
    )
    nomenclature = StringField(
        validators=[Length(max=100)],
        description='максимум 100 символов'
    )
    room_use_etalon = ExtendedSelectField(coerce=int, model='Room')
    place = ExtendedSelectField(coerce=int, model='Place')
    control_vp = BooleanField(default=False)
    room_delivery = ExtendedSelectField(coerce=int, model='Room')
    employee = ExtendedSelectField(coerce=int, model='Employee')
    division = StringField(render_kw={'readonly': True})
    email = StringField(render_kw={'readonly': True})
    date_last_service = DateField()
    date_next_service = DateField()
    certificate = ExtendedFileField(upload='certificate/')
    is_service = BooleanField(default=False, render_kw={'readonly': True})


class ServiceForm(SiteForm):
    """Обслуживание СИ"""

    date_in_service = DateField(render_kw={'readonly': True})
    date_out_service = DateField(validators=[Optional()])
    date_last_service = DateField(
        validators=[Optional()], render_kw={'readonly': True}
    )
    date_next_service = DateField(validators=[Optional()])
    is_ready = BooleanField(default=False)
    certificate = ExtendedFileField(upload='certificate/')
    note = TextAreaField(
        validators=[Length(max=1000)], description='максимум 1000 символов'
    )


class AddServiceForm(SiteForm):
    """Добавление СИ на обслуживание"""

    date_in_service = DateField(validators=[DataRequired()])


class OutServiceForm(SiteForm):
    """Выдача СИ с обслуживания"""

    date_out_service = DateField()
    date_next_service = DateField()
    certificate = ExtendedFileField(upload='certificate/')
    note = TextAreaField(
        validators=[Length(max=1000)], description='максимум 1000 символов'
    )
