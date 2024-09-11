from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo, ValidationError

from src.auth import password_validation
from src.core import SiteForm


class LoginForm(FlaskForm):
    username = StringField(
        label='Имя пользователя:',
        validators=[
            InputRequired(),
        ],
    )
    password = StringField(
        label='Пароль:',
        validators=[
            InputRequired(),
        ],
    )

    is_active = True


class PasswordChangeForm(SiteForm):
    password = PasswordField(
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

    def update_instance(self):
        instance = super().update_instance()
        if instance.password:
            instance.password = current_user.hash_password(instance.password)
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
