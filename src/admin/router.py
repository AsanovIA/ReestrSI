from flask import Blueprint, redirect, url_for

from src.admin.views import IndexView
from src.service.router import router_si
from src.service.router import router_service
from src.datasource.router import router as router_datasource
from src.users.router import router as router_users

router = Blueprint(
    'admin',
    __name__,
    template_folder='template',
    static_folder='static',
    url_prefix='/admin',
)

settings = Blueprint('settings', __name__, url_prefix='/settings')

router.register_blueprint(settings)
router.register_blueprint(router_service)
router.register_blueprint(router_si)

settings.register_blueprint(router_datasource)
settings.register_blueprint(router_users)

settings.add_url_rule("/",
                      view_func=IndexView.as_view(
                          name="index",
                          blueprint_name=settings.name,
                      ))


@router.route('/')
def index():
    return redirect(url_for('admin.si.list_si'))
