import os
import sys

from flask import Flask

from src.config import settings

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from src.admin.router import router as router_admin
from src.device.router import router as router_device
from src.source.router import router as router_source

app = Flask(__name__)

app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['WTF_I18N_ENABLED'] = False

app.register_blueprint(router_admin)
app.register_blueprint(router_device)
app.register_blueprint(router_source)


if __name__ == "__main__":
    if '--db_default' in sys.argv:
        from src.db.default.db_restore import set_default_db
        set_default_db()
