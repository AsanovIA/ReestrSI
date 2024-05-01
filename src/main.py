import os
import sys

from flask import Flask
from flask_login import LoginManager

from src.auth.UserLogin import UserLogin
from src.config import settings

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from src.admin.router import router as router_admin
from src.auth.router import router as router_auth
from src.device.router import router as router_device
from src.source.router import router as router_source

app = Flask(__name__)

app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['WTF_I18N_ENABLED'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'

app.register_blueprint(router_admin)
app.register_blueprint(router_auth)
app.register_blueprint(router_device)
app.register_blueprint(router_source)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().get_user(user_id)


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == "__main__":
    if '--db_default' in sys.argv:
        from src.db.default.db_restore import set_default_db

        set_default_db()
