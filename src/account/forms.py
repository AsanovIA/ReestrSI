from wtforms.fields import PasswordField
from wtforms.validators import InputRequired

from src.auth.forms import PasswordChangeForm
from src.core.validators import OldPassword


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = PasswordField(
        label='Старый пароль',
        validators=[InputRequired(), OldPassword()],
    )

    class Meta:
        fields = ['old_password', 'password', 'password2']
