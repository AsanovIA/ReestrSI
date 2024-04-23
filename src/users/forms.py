from flask_wtf import FlaskForm
from wtforms.fields.simple import (
    BooleanField,
    EmailField,
    PasswordField,
    StringField,
)
from wtforms.validators import Length, Email, Optional, DataRequired


class UserProfileForm(FlaskForm):
    username = StringField(
        label='Логин',
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    password = PasswordField(
        label='Пароль',
        render_kw={'readonly': True},
    )
    last_name = StringField(
        label='Фамилия',
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    first_name = StringField(
        label='Имя',
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    middle_name = StringField(
        label='Отчество',
        validators=[DataRequired(), Length(max=100)],
        description='максимум 100 символов'
    )
    email = EmailField(
        label='e-mail',
        validators=[Email(), Optional()]
    )
    is_active = BooleanField(
        label='Активный',
        description='Отметьте, если пользователь должен считаться активным. '
                    'Уберите эту отметку вместо удаления учётной записи.'
    )
