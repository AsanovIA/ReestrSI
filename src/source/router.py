from flask import Blueprint

from src.source.views import ValueChangeView

router = Blueprint('source', __name__, url_prefix='/')


router.add_url_rule('/valuechange/',
                    view_func=ValueChangeView.as_view(name="valuechange"))
