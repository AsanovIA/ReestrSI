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

    APPS: List[str] = [
        'datasource',
        'service',
        'users',
    ]

    LANGUAGE: str = 'ru'
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
