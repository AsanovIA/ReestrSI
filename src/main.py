import os
import sys

from flask import Flask

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from src.admin.router import router as router_admin

app = Flask(__name__)

app.register_blueprint(router_admin)
app.config['SECRET_KEY'] = 'secret_key'
app.config['WTF_I18N_ENABLED'] = False


if __name__ == "__main__":
    if '--db_default' in sys.argv:
        from src.db.default.db_restore import set_default_db
        set_default_db()
