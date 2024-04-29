from werkzeug.security import generate_password_hash
from wtforms.fields import (
    BooleanField, EmailField, Field, PasswordField, StringField,
)
from wtforms.validators import Length, Email, Optional, DataRequired, \
    EqualTo, InputRequired, ValidationError

from src.auth import password_validation
from src.forms import SiteForm
from src.validators import Unique
from src.widgets import DivWidget


class ReadOnlyPasswordHashWidget(DivWidget):
    def __call__(self, field, **kwargs):
        if not field.data:
            text = "Пароль не установлен."
        else:
            text = ''
            for key, value_ in self.safe_summary(field.data).items():
                text += f'<strong>{key}</strong>'
                text += f': <bdi>{value_}</bdi> ' if value_ else ' '
        self.text = text
        return super().__call__(field, **kwargs)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        return {
            'алгоритм': algorithm,
            'соль': self.mask_hash(salt),
            'хэш': self.mask_hash(hash),
        }

    def mask_hash(self, hash, show=6, char="*"):
        masked = hash[:show]
        masked += char * 10
        return masked


class ReadOnlyPasswordHashField(Field):
    widget = ReadOnlyPasswordHashWidget()


class UserProfileForm(SiteForm):
    username = StringField(
        label='Логин',
        validators=[DataRequired(), Length(max=100), Unique()],
        description='максимум 100 символов'
    )
    password = ReadOnlyPasswordHashField(
        label='Пароль',
        description='Пароли хранятся в зашифрованном виде, поэтому нет '
                    'возможности посмотреть пароль этого пользователя, но вы '
                    'можете изменить его используя '
                    '<a href="{}">эту форму</a>.'
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

    class Meta:
        exclude = [
            'password',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.password
        if password.data:
            password.description = password.description.format('./password/')


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
        description=password_validation.password_validators_description_html(),
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

    def update_instance(self):
        instance = super().update_instance()
        if instance.password:
            instance.password = generate_password_hash(instance.password)
        return instance

    def post_validate(self):
        success = super().post_validate()
        password = self.data.get('password')
        try:
            password_validation.validate_password(password, self.instance)
        except ValidationError as e:
            self.password.errors.extend(e.args[0])
            return False
        return success
