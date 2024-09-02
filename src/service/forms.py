from wtforms import (
    DateField, IntegerField, StringField, BooleanField, TextAreaField
)
from wtforms.validators import Length, NumberRange, Optional, DataRequired

from src.core import (
    MAX_LENGTH, MAX_LENGTH_TEXTAREA, SiteForm, ExtendedFileField,
    ExtendedSelectField, UniqueFile
)


class SiForm(SiteForm):
    """Средство измерения"""

    group_si = ExtendedSelectField(
        model='GroupSi',
        validators=[DataRequired()]
    )
    name_si = ExtendedSelectField(model='NameSi', validators=[DataRequired()])
    type_si = ExtendedSelectField(model='TypeSi', validators=[DataRequired()])
    number = StringField(
        validators=[DataRequired(), Length(max=MAX_LENGTH)],
        description=f'максимум {MAX_LENGTH} символов'
    )
    description_method = ExtendedSelectField(model='DescriptionMethod')
    description = StringField()
    method = StringField()
    service_type = ExtendedSelectField(
        model='ServiceType',
        validators=[DataRequired()]
    )
    service_interval = ExtendedSelectField(
        model='ServiceInterval',
        validators=[DataRequired()]
    )
    etalon = BooleanField(default=False)
    category_etalon = StringField(
        validators=[Length(max=MAX_LENGTH)],
        description=f'максимум {MAX_LENGTH} символов'
    )
    year_production = IntegerField(
        validators=[NumberRange(min=1900, max=2200), Optional()],
        description='диапазон от 1900 до 2200',
    )
    nomenclature = StringField(
        validators=[Length(max=MAX_LENGTH)],
        description=f'максимум {MAX_LENGTH} символов'
    )
    room_use_etalon = ExtendedSelectField(model='Room')
    place = ExtendedSelectField(model='Place')
    control_vp = BooleanField(default=False)
    employee = ExtendedSelectField(model='Employee')
    division = StringField()
    email = StringField()
    room_delivery = ExtendedSelectField(model='Room')
    date_last_service = DateField(validators=[Optional()])
    date_next_service = DateField(validators=[DataRequired()])
    certificate = ExtendedFileField(validators=[DataRequired(), UniqueFile()])
    status_service = StringField()

    class Meta:
        readonly_fields = [
            'description', 'method', 'division', 'email', 'status_service',
        ]

    def get_readonly_fields(self, readonly_fields=None):
        if self.instance.is_service:
            readonly_fields = [
                'date_last_service', 'date_next_service', 'certificate'
            ]
        return super().get_readonly_fields(readonly_fields)


class ServiceForm(SiteForm):
    """Обслуживание СИ"""

    date_in_service = DateField(validators=[Optional()])
    date_last_service = DateField(validators=[Optional()])
    date_next_service = DateField(validators=[Optional()])
    status_service = ExtendedSelectField(
        model='StatusService',
        validators=[DataRequired()]
    )
    certificate = ExtendedFileField(validators=[UniqueFile()])
    note = TextAreaField(
        validators=[Length(max=MAX_LENGTH_TEXTAREA)],
        description=f'максимум {MAX_LENGTH_TEXTAREA} символов'
    )

    class Meta:
        readonly_fields = ['date_in_service', 'date_last_service']


class AddServiceForm(SiteForm):
    """Добавление СИ на обслуживание"""

    date_in_service = DateField(validators=[DataRequired()])
    status_service = ExtendedSelectField(
        model='StatusService',
        validators=[DataRequired()]
    )


class OutServiceForm(SiteForm):
    """Выдача СИ с обслуживания"""

    date_out_service = DateField(validators=[DataRequired()])
    date_next_service = DateField(validators=[DataRequired()])
    certificate = ExtendedFileField(validators=[DataRequired(), UniqueFile()])
    note = TextAreaField(
        validators=[Length(max=MAX_LENGTH_TEXTAREA)],
        description=f'максимум {MAX_LENGTH_TEXTAREA} символов'
    )
