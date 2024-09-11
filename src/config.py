import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

NAMESUBD = 'sqlite'
# NAMESUBD = 'postgres'


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    SECRET_KEY: str

    BASEDIR: str = os.path.dirname(os.path.abspath(__file__))
    ALLOWED_EXTENSIONS: List[str] = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
    ALLOWED_SYMBOLS_CONTENT: List[str] = [
        'A-Z', 'a-z', '0-9', '_', '-', '"точка" .'
    ]
    MAX_CONTENT_LENGTH: int = 100
    UPLOAD_FOLDER: str = os.path.join(BASEDIR, 'uploads')

    APPS: List[str] = [
        'src.service',
        'src.datasource',
        'src.users',
        'src.account',
    ]

    AUTH_PASSWORD_VALIDATORS: List[dict] = [
        {'NAME': 'src.auth.password_validation.AttributeSimilarityValidator'},
        {
            'NAME': 'src.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {'min_length': 6},
        },
        {'NAME': 'src.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'src.auth.password_validation.NumericPasswordValidator'},
    ]

    LANGUAGES: List[str] = ['ru', 'en']
    SITE_NAME: str = 'Средства измерения'

    @property
    def DATABASE_URL(self):
        if NAMESUBD == 'sqlite':
            path = os.path.join(self.BASEDIR, "db", "reestrsi.db")
            return f'sqlite:///{path}'
        elif NAMESUBD == 'postgres':
            return (f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@"
                    f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    model_config = SettingsConfigDict(env_file=f"{BASEDIR}/../.env")


settings = Settings()
