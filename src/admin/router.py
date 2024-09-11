from flask import Blueprint, redirect, url_for, request
from flask_login import current_user

from src.admin.views import IndexView
from src.account.router import router as router_account
from src.service.router import router_service, router_si
from src.datasource.router import router as router_datasource
from src.users.router import router as router_users

router = Blueprint(
    'admin',
    __name__,
    template_folder='template',
    static_folder='static',
    url_prefix='/admin',
)

router.register_blueprint(router_account)
router.register_blueprint(router_service)
router.register_blueprint(router_si)

settings = Blueprint('settings', __name__, url_prefix='/settings')

router.register_blueprint(settings)

settings.register_blueprint(router_datasource)
settings.register_blueprint(router_users)


@router.before_request
def admin_before_request():
    # Проверка аутентификации пользователя
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))


settings.add_url_rule("/",
                      view_func=IndexView.as_view(
                          name="index",
                          blueprint_name=settings.name,
                      ))


@router.route('/')
def index():
    return redirect(url_for('admin.si.list_si'))
