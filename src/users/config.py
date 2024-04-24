from src.users.models import (
    UserProfile
)

app_settings = {
    'name': 'users',
    'verbose_name': 'Пользователи',
    'models': {
        'UserProfile'.lower(): UserProfile,
    }
}
