from markupsafe import Markup
from werkzeug.security import generate_password_hash
from wtforms.fields.simple import (
    BooleanField,
    EmailField,
    PasswordField,
    StringField,
)
from wtforms.validators import Length, Email, Optional, DataRequired, EqualTo, \
    InputRequired

from src.forms import SiteForm
from src.validators import Unique


class UserProfileForm(SiteForm):
    username = StringField(
        label='Логин',
        validators=[DataRequired(), Length(max=100), Unique()],
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
        validators=[
            Email(),
            Unique(message='Пользователь с таким e-mail уже существует'),
            Optional(),
        ]
    )
    is_active = BooleanField(
        label='Активный',
        description='Отметьте, если пользователь должен считаться активным. '
                    'Уберите эту отметку вместо удаления учётной записи.'
    )


class AddUserForm(SiteForm):
    username = StringField(
        label='Логин',
        validators=[DataRequired(), Length(max=100), Unique()],
        description='максимум 100 символов'
    )
    password = PasswordField(
        label='Пароль',
        validators=[
            InputRequired(),
            EqualTo(fieldname='password2', message='Пароли не совпадают'),
        ],
    )
    password2 = PasswordField(
        label='Подтверждение пароля',
        validators=[InputRequired()],
        description='Для подтверждения введите, пожалуйста, пароль ещё раз.'
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
        validators=[
            Email(),
            Unique(message='Пользователь с таким e-mail уже существует'),
            Optional(),
        ]
    )
