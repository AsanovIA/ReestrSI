import datetime

from sqlalchemy import create_engine, func, String, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from typing_extensions import Annotated

from src.config import settings, NAMESUBD

engine = create_engine(
    url=settings.DATABASE_URL,
    # echo=True,
)

session_factory = sessionmaker(engine)

if NAMESUBD == 'sqlite':
    created_at = Annotated[datetime.datetime, mapped_column(
        server_default=func.CURRENT_TIMESTAMP()
    )]
elif NAMESUBD == 'postgres':
    created_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )]


str_100 = Annotated[str, 100]
str_256 = Annotated[str, 256]
str_1000 = Annotated[str, 1000]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_100: String(100),
        str_256: String(256),
        str_1000: String(1000),
    }

    repr_cols_num = 3
    repr_cols = tuple()

    class Meta:
        action_suffix = ''

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class BasePK:
    id: Mapped[int] = mapped_column(primary_key=True)
