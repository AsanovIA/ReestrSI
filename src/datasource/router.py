from flask import Blueprint

from src.datasource.views import (
    IndexView, ListObjectView, ChangeObjectView, AddObjectView,
    DeleteObjectView
)

router = Blueprint('datasource', __name__, url_prefix='/datasource')

router.add_url_rule("/",
                    view_func=IndexView.as_view(
                        name="index",
                        blueprint_name=router.name,
                    ))

router.add_url_rule("/<model_name>/",
                    view_func=ListObjectView.as_view(
                        name=f"list_{router.name}",
                        blueprint_name=router.name,
                    ))

router.add_url_rule("/<model_name>/<int:pk>/",
                    view_func=ChangeObjectView.as_view(
                        name=f"change_{router.name}",
                        blueprint_name=router.name,
                    ))

router.add_url_rule("/<model_name>/add/",
                    view_func=AddObjectView.as_view(
                        name=f"add_{router.name}",
                        blueprint_name=router.name,
                    ))

router.add_url_rule("/<model_name>/<int:pk>/delete/",
                    view_func=DeleteObjectView.as_view(
                        name=f"delete_{router.name}",
                        blueprint_name=router.name,
                    ))
