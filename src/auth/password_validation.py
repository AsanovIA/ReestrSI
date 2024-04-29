import gzip
import re

from werkzeug.utils import import_string
from wtforms.validators import ValidationError
from markupsafe import Markup
from difflib import SequenceMatcher
from pathlib import Path

from src.config import settings
from src.utils import format_html, get_suffix, label_for_field


def get_default_password_validators():
    return get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)


def get_password_validators(validator_config):
    validators = []
    for validator in validator_config:
        try:
            klass = import_string(validator["NAME"])
        except ImportError:
            msg = (
                "Не удалось импортировать модуль NAME: %s. Проверти "
                "AUTH_PASSWORD_VALIDATORS в настройках."
            )
            raise ImportError(msg % validator["NAME"])
        validators.append(klass(**validator.get("OPTIONS", {})))

    return validators


def validate_password(password, user=None, password_validators=None):
    errors = []
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            errors.append(error)
    if errors:
        raise ValidationError(errors)


def password_validators_descriptions(password_validators=None):
    """
    Return a list of all help texts of all configured validators.
    """
    help_texts = []
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        help_texts.append(validator.get_help_text())
    return help_texts


def _password_validators_description_html(password_validators=None):
    """
    Return an HTML string with all help texts of all configured validators
    in an <ul>.
    """
    help_texts = password_validators_descriptions(password_validators)
    help_items = Markup("".join(
        format_html("<li>{}</li>", help_text) for help_text in help_texts
    ))
    return format_html('<ul>{}</ul>', help_items) if help_items else ''


password_validators_description_html = _password_validators_description_html


class MinimumLengthValidator:
    """
    Validate that the password is of a minimum length.
    """

    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                "Введённый пароль слишком короткий. Он должен содержать как "
                "минимум %(min_length)d %(new_text)s." % {
                    "min_length": self.min_length,
                    "new_text": get_suffix('символ', self.min_length)
                })

    def get_help_text(self):
        return ("Ваш пароль должен содержать как минимум %(min_length)d "
                "%(new_text)s.") % {
            "min_length": self.min_length,
            "new_text": get_suffix('символ', self.min_length)
        }


def exceeds_maximum_length_ratio(password, max_similarity, value):
    """
    Test that value is within a reasonable range of password.

    The following ratio calculations are based on testing SequenceMatcher like
    this:

    for i in range(0,6):
      print(10**i, SequenceMatcher(a='A', b='A'*(10**i)).quick_ratio())

    which yields:

    1 1.0
    10 0.18181818181818182
    100 0.019801980198019802
    1000 0.001998001998001998
    10000 0.00019998000199980003
    100000 1.999980000199998e-05

    This means a length_ratio of 10 should never yield a similarity higher than
    0.2, for 100 this is down to 0.02 and for 1000 it is 0.002. This can be
    calculated via 2 / length_ratio. As a result we avoid the potentially
    expensive sequence matching.
    """
    pwd_len = len(password)
    length_bound_similarity = max_similarity / 2 * pwd_len
    value_len = len(value)
    return pwd_len >= 10 * value_len and value_len < length_bound_similarity


class AttributeSimilarityValidator:
    """
    Validate that the password is sufficiently different from the user's
    attributes.

    If no specific attributes are provided, look at a sensible list of
    defaults. Attributes that don't exist are ignored. Comparison is made to
    not only the full attribute value, but also its components, so that, for
    example, a password is validated against either part of an email address,
    as well as the full address.
    """

    DEFAULT_USER_ATTRIBUTES = (
        "username", "first_name", "middle_name", "last_name", "email"
    )

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_attributes = user_attributes
        if max_similarity < 0.1:
            raise ValueError("max_similarity must be at least 0.1")
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        password = password.lower()
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_lower = value.lower()
            value_parts = re.split(r"\W+", value_lower) + [value_lower]
            for value_part in value_parts:
                if exceeds_maximum_length_ratio(
                    password, self.max_similarity, value_part
                ):
                    continue
                if (
                    SequenceMatcher(a=password, b=value_part).quick_ratio()
                    >= self.max_similarity
                ):
                    verbose_name = label_for_field(attribute_name)
                    raise ValidationError(
                        ("Введённый пароль слишком похож на %(verbose_name)s."
                         ) % {"verbose_name": verbose_name}
                    )

    def get_help_text(self):
        return ("Пароль не должен быть слишком похож на другую вашу "
                "личную информацию.")


class CommonPasswordValidator:
    """
    Validate that the password is not a common password.

    The password is rejected if it occurs in a provided list of passwords,
    which may be gzipped. The list Django ships with contains 20000 common
    passwords (lowercased and deduplicated), created by Royce Williams:
    https://gist.github.com/roycewilliams/226886fd01572964e1431ac8afc999ce
    The password list must be lowercased to match the comparison in validate().
    """

    def DEFAULT_PASSWORD_LIST_PATH(self):
        return Path(__file__).resolve().parent / "common-passwords.txt.gz"
    
    def __init__(self, password_list_path=DEFAULT_PASSWORD_LIST_PATH):
        if password_list_path is CommonPasswordValidator.DEFAULT_PASSWORD_LIST_PATH:
            password_list_path = self.DEFAULT_PASSWORD_LIST_PATH()
        try:
            with gzip.open(password_list_path, "rt", encoding="utf-8") as f:
                self.passwords = {x.strip() for x in f}
        except OSError:
            with open(password_list_path) as f:
                self.passwords = {x.strip() for x in f}

    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                "Введённый пароль слишком широко распространён."
            )

    def get_help_text(self):
        return "Пароль не должен быть слишком простым и распространенным."


class NumericPasswordValidator:
    """
    Validate that the password is not entirely numeric.
    """

    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError("Введённый пароль состоит только из цифр.")

    def get_help_text(self):
        return "Пароль не может состоять только из цифр."
