from flask import Blueprint

from src.service.views import (
    ListSiView, ChangeSiView, AddSiView,
    ListServiceView, ChangeServiceView, AddServiceView, OutServiceView,
    HistoryServiceView
)

router_si = Blueprint('si', __name__, url_prefix='/si')
router_service = Blueprint('service', __name__, url_prefix='/service')

router_si.add_url_rule("/",
                       view_func=ListSiView.as_view(
                           name=f"list_{router_si.name}",
                           blueprint_name=router_si.name,
                       ))

router_si.add_url_rule("/<int:pk>/",
                       view_func=ChangeSiView.as_view(
                           name=f"change_{router_si.name}",
                           blueprint_name=router_si.name,
                       ))

router_si.add_url_rule("/add/",
                       view_func=AddSiView.as_view(
                           name=f"add_{router_si.name}",
                           blueprint_name=router_si.name,
                       ))

router_si.add_url_rule("/<int:pk>/service/",
                       view_func=AddServiceView.as_view(
                           name=f"add_service",
                           blueprint_name=router_si.name,
                       ))

router_service.add_url_rule("/",
                            view_func=ListServiceView.as_view(
                                name=f"list_{router_service.name}",
                                blueprint_name=router_service.name,
                            ))

router_service.add_url_rule("/<int:pk>/",
                            view_func=ChangeServiceView.as_view(
                                name=f"change_{router_service.name}",
                                blueprint_name=router_service.name,
                            ))

router_service.add_url_rule("/<int:pk>/out/",
                            view_func=OutServiceView.as_view(
                                name=f"out_{router_service.name}",
                                blueprint_name=router_service.name,
                            ))

router_service.add_url_rule("/<int:pk>/history/",
                            view_func=HistoryServiceView.as_view(
                                name=f"history_{router_service.name}",
                                blueprint_name=router_service.name,
                            ))
