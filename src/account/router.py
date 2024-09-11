from flask import Blueprint

from src.account.views import UserPasswordChangeView

router = Blueprint('account', __name__, url_prefix='/account')

router.add_url_rule("/password_change/",
                    view_func=UserPasswordChangeView.as_view(
                        name=f"password_change",
                        blueprint_name=router.name,
                    ))
