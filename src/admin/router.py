from flask import Blueprint, redirect, url_for

from src.datasource.router import router as router_datasource
from src.users.router import router as router_users
from src.admin.views import IndexView

router = Blueprint(
    'admin',
    __name__,
    template_folder='template',
    static_folder='static',
    url_prefix='/admin',
)
settings = Blueprint('settings', __name__, url_prefix='/settings')

router.register_blueprint(settings)

settings.register_blueprint(router_datasource)
settings.register_blueprint(router_users)

settings.add_url_rule("/",
                      view_func=IndexView.as_view(
                          name="index",
                          blueprint_name=settings.name,
                      ))


@router.route('/')
def index():
    return redirect(url_for('admin.settings.index'))
