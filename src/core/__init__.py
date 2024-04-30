from src.core.fields import ExtendedSelectField
from src.core.forms import SiteForm
from src.core.media import Media
from src.core.mixins import (
    AddMixin,
    ChangeMixin,
    DeleteMixin,
    FormMixin,
    IndexMixin,
    ListMixin,
    SettingsMixin,
    SiteMixin
)
from src.core.suffixes import update_suffix
from src.core.utils import (
    BLANK_CHOICE,
    EMPTY_VALUE_DISPLAY,
    FIELDS_EXCLUDE,
    SETTINGS_APP_LIST,
    boolean_icon,
    display_for_field,
    display_for_value,
    format_html,
    get_app_settings,
    get_form_class,
    get_model,
    get_suffix,
    label_for_field,
    lookup_field,
    try_get_url
)
from src.core.validators import Unique
from src.core.widgets import DivWidget
