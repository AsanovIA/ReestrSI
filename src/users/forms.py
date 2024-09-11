from flask import g
from wtforms.fields import BooleanField, EmailField, Field, StringField
from wtforms.validators import Length, Email, Optional, DataRequired

from src.auth.forms import PasswordChangeForm
from src.core import MAX_LENGTH, DivWidget, SiteForm, Unique


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
        validators=[DataRequired(), Length(max=MAX_LENGTH), Unique()],
        description=f'максимум {MAX_LENGTH} символов'
    )
    password = ReadOnlyPasswordHashField(
        description='Пароли хранятся в зашифрованном виде, поэтому нет '
                    'возможности посмотреть пароль этого пользователя, но вы '
                    'можете изменить его используя '
                    '<a href="{}">эту форму</a>.'
    )
    last_name = StringField(
        validators=[DataRequired(), Length(max=MAX_LENGTH)],
        description=f'максимум {MAX_LENGTH} символов'
    )
    first_name = StringField(
        validators=[DataRequired(), Length(max=MAX_LENGTH)],
        description=f'максимум {MAX_LENGTH} символов'
    )
    middle_name = StringField(
        validators=[DataRequired(), Length(max=MAX_LENGTH)],
        description=f'максимум {MAX_LENGTH} символов'
    )
    email = EmailField(
        validators=[
            Email(),
            Unique(message='Пользователь с таким e-mail уже существует'),
            Optional(),
        ]
    )
    is_active = BooleanField(
        description='Отметьте, если пользователь должен считаться активным. '
                    'Уберите эту отметку вместо удаления учётной записи.'
    )
    is_superuser = BooleanField(
        description='Указывает, что пользователь имеет все права без явного '
                    'их назначения.'
    )

    class Meta:
        pass

    def __init__(self, *args, **kwargs):
        if not g.user.is_superuser:
            self.Meta.exclude = ['is_superuser']
        super().__init__(*args, **kwargs)
        password = self.password
        if password.data:
            password.description = password.description.format('./password/')


class AddUserForm(PasswordChangeForm, UserProfileForm):
    class Meta:
        fields = [
            'username',
            'password',
            'password2',
            'last_name',
            'first_name',
            'middle_name',
            'email',
        ]


class AdminPasswordChangeForm(PasswordChangeForm):
    pass
