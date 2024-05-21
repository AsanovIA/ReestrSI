from wtforms import (
    DateField, IntegerField, StringField, BooleanField, TextAreaField
)
from wtforms.validators import Length, NumberRange, Optional, DataRequired

from src.core import SiteForm, ExtendedFileField, ExtendedSelectField


class SiForm(SiteForm):
    """Средство измерения"""

    group_si = ExtendedSelectField(
        model='GroupSi', validators=[DataRequired()]
    )
    name_si = ExtendedSelectField(model='NameSi', validators=[DataRequired()])
    type_si = ExtendedSelectField(model='TypeSi', validators=[DataRequired()])
    number = StringField(
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    description_method = ExtendedSelectField(model='DescriptionMethod')
    description = StringField()
    method = StringField()
    service_type = ExtendedSelectField(
        model='ServiceType', validators=[DataRequired()]
    )
    service_interval = ExtendedSelectField(
        model='ServiceInterval', validators=[DataRequired()]
    )
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
    room_use_etalon = ExtendedSelectField(model='Room')
    place = ExtendedSelectField(model='Place')
    control_vp = BooleanField(default=False)
    employee = ExtendedSelectField(model='Employee')
    division = StringField()
    email = StringField()
    room_delivery = ExtendedSelectField(model='Room')
    date_last_service = DateField(validators=[Optional()])
    date_next_service = DateField(validators=[Optional()])
    certificate = ExtendedFileField()
    status_service = ExtendedSelectField(
        model='StatusService', validators=[Optional()]
    )
    is_service = BooleanField(default=False)

    class Meta:
        readonly_fields = [
            'description', 'method', 'division', 'email', 'status_service',
            'is_service'
        ]


class ServiceForm(SiteForm):
    """Обслуживание СИ"""

    date_in_service = DateField(validators=[Optional()])
    date_last_service = DateField(validators=[Optional()])
    date_next_service = DateField(validators=[Optional()])
    status_service = ExtendedSelectField(model='StatusService')
    certificate = ExtendedFileField()
    note = TextAreaField(
        validators=[Length(max=1000)], description='максимум 1000 символов'
    )

    class Meta:
        readonly_fields = ['date_in_service', 'date_last_service']


class AddServiceForm(SiteForm):
    """Добавление СИ на обслуживание"""

    date_in_service = DateField(validators=[DataRequired()])
    status_service = ExtendedSelectField(
        model='StatusService', validators=[DataRequired()]
    )


class OutServiceForm(SiteForm):
    """Выдача СИ с обслуживания"""

    date_out_service = DateField(validators=[DataRequired()])
    date_next_service = DateField(validators=[DataRequired()])
    certificate = ExtendedFileField(validators=[DataRequired()])
    note = TextAreaField(
        validators=[Length(max=1000)], description='максимум 1000 символов'
    )
