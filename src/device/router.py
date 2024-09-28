from flask import Blueprint, redirect, url_for
from flask_login import current_user

from src.device.views import (
    UserListSiView,
    UserObjectSiView,
    UserHistoryServiceView
)

router = Blueprint('device', __name__, url_prefix='/')


@router.before_request
def check_authorization():
    if current_user.is_authenticated:
        return redirect(url_for('admin.si.list_si'))


router.add_url_rule("",
                    view_func=UserListSiView.as_view(
                        name="index",
                        blueprint_name=router.name,
                    ))

router.add_url_rule('/<int:pk>/',
                    view_func=UserObjectSiView.as_view(
                        name=f"view_{router.name}",
                        blueprint_name=router.name,
                    ))

router.add_url_rule('/<int:pk>/history/',
                    view_func=UserHistoryServiceView.as_view(
                        name=f"history_{router.name}",
                        blueprint_name=router.name,
                    ))
