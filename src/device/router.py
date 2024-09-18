from flask import Blueprint

from src.device.views import ListObjectView, ViewSiView
from src.service.views import HistoryServiceView

router = Blueprint('device', __name__, url_prefix='/')

router.add_url_rule("",
                    view_func=ListObjectView.as_view(
                        name="index",
                        blueprint_name=router.name,
                    ))

router.add_url_rule('/<int:pk>/',
                    view_func=ViewSiView.as_view(
                        name=f"view_{router.name}",
                        blueprint_name=router.name,
                    ))

router.add_url_rule('/<int:pk>/history/',
                    view_func=HistoryServiceView.as_view(
                        name=f"history_{router.name}",
                        blueprint_name=router.name,
                    ))
