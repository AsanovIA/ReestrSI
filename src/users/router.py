from flask import Blueprint

from src.users.views import (
    ListObjectView, ChangeObjectView, AddObjectView, DeleteObjectView
)

router = Blueprint('users', __name__, url_prefix='/users')

router.add_url_rule("/",
                    view_func=ListObjectView.as_view(
                        name=f"list_{router.name}",
                        blueprint_name=router.name,
                    ))

router.add_url_rule("/<int:pk>/",
                    view_func=ChangeObjectView.as_view(
                        name=f"change_{router.name}",
                        blueprint_name=router.name,
                    ))

router.add_url_rule("/add/",
                    view_func=AddObjectView.as_view(
                        name=f"add_{router.name}",
                        blueprint_name=router.name,
                    ))

router.add_url_rule("/<int:pk>/delete/",
                    view_func=DeleteObjectView.as_view(
                        name=f"delete_{router.name}",
                        blueprint_name=router.name,
                    ))
