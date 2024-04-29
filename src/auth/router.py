from flask import render_template, redirect, url_for, request, Blueprint
from flask_login import logout_user, login_required, login_user, current_user
from sqlalchemy.exc import NoResultFound
from werkzeug.security import check_password_hash

from src.auth.forms import LoginForm
from src.auth.UserLogin import UserLogin
from src.db.repository import Repository
from src.utils import get_model

router = Blueprint('auth', __name__, url_prefix='/account')


@router.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        model = get_model('userprofile')
        try:
            user = Repository.task_get_object(
                model=model, filters={'username': form.username.data}
            )
        except NoResultFound:
            form.username.errors.append(
                'Пользователя с таким логином не существует')
        else:
            if not check_password_hash(user.password, form.password.data):
                form.password.errors.append('неверный пароль')
            elif user.is_active:
                auth_user = UserLogin().create(user)
                login_user(auth_user)

                next = request.args.get('next')

                return redirect(next or url_for('admin.index'))

            else:
                form.is_active = False
                form.username.errors.append('Пользователь не активен')

    return render_template('login.html', form=form)


@router.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('device.index'))
