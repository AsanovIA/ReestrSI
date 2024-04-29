from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired


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
