from flask import Blueprint, current_app, send_file
from werkzeug.security import safe_join

from src.source.views import ValueChangeView

router = Blueprint('source', __name__, url_prefix='/')


router.add_url_rule('/valuechange/',
                    view_func=ValueChangeView.as_view(name="valuechange"))


@router.route('/view/<path:filename>')
def view_file(filename):
    path = safe_join(current_app.config["UPLOAD_FOLDER"], filename)
    return send_file(path)
