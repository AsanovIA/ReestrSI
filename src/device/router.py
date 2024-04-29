from flask import Blueprint

from src.device.views import ListObjectView

router = Blueprint('device', __name__, url_prefix='/')

router.add_url_rule("",
                    view_func=ListObjectView.as_view(
                        name="index",
                        blueprint_name=router.name,
                    ))
