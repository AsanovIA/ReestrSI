from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base, BasePK, str_100, created_at


class UserProfile(BasePK, Base):
    """Пользователь"""
    __tablename__ = "userprofile"

    username: Mapped[str_100]
    password: Mapped[str]
    last_name: Mapped[str_100]
    first_name: Mapped[str_100]
    middle_name: Mapped[str_100]
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    date_joined: Mapped[created_at] = mapped_column(doc='Дата регистрации')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        fields_display = [
            'username', 'get_full_name', 'email', 'is_active', 'date_joined',
        ]

    def __repr__(self):
        return self.username

    def get_full_name(self):
        # Формирование полного имени "Фамилия Имя Отчество"
        full_name = "%s %s %s" % (self.last_name,
                                  self.first_name,
                                  self.middle_name
                                  )
        return full_name.strip()

    get_full_name.short_description = 'Ф.И.О.'

    def get_short_name(self):
        # Формирование имени "Фамилия И.О."
        try:
            short_name = '%s %s.%s.' % (str(self.last_name).capitalize(),
                                        str(self.first_name)[0].upper(),
                                        str(self.middle_name)[0].upper(),
                                        )
        except IndexError:
            return str(self.last_name).capitalize()

        return short_name
