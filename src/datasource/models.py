from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base, BasePK, str_100, str_256


class BaseName(BasePK):
    name: Mapped[str_256] = mapped_column(
        info={'label': 'Наименование'}, unique=True)

    class Meta:
        fields_display = ['name']
        ordering = ('name',)

    def __str__(self):
        return str(self.name)


class GroupSi(BaseName, Base):
    """Группы СИ по областям и разделам областей измерений"""
    __tablename__ = "group_si"

    si: Mapped["Si"] = relationship(back_populates="group_si")

    class Meta(BaseName.Meta):
        verbose_name = 'Группа СИ'
        verbose_name_plural = 'Группы СИ'
        verbose_name_change = 'Группу СИ'


class NameSi(BaseName, Base):
    """Наименование СИ"""
    __tablename__ = "name_si"

    si: Mapped["Si"] = relationship(back_populates="name_si")

    class Meta(BaseName.Meta):
        verbose_name = 'Наименование СИ'
        verbose_name_plural = 'Наименования СИ'


class TypeSi(BaseName, Base):
    """Тип СИ"""
    __tablename__ = "type_si"

    si: Mapped["Si"] = relationship(back_populates="type_si")

    class Meta(BaseName.Meta):
        verbose_name = 'Тип СИ'
        verbose_name_plural = 'Типы СИ'


class ServiceType(BaseName, Base):
    """Вид метрологического обслуживания"""
    __tablename__ = "service_type"

    si: Mapped["Si"] = relationship(back_populates="service_type")

    class Meta(BaseName.Meta):
        verbose_name = 'Вид метрологического обслуживания'
        verbose_name_plural = 'Виды метрологического обслуживания'


class ServiceInterval(BaseName, Base):
    """Интервал обслуживания"""
    __tablename__ = "service_interval"

    name: Mapped[int]

    si: Mapped["Si"] = relationship(back_populates="service_interval")

    class Meta(BaseName.Meta):
        verbose_name = 'Интервал обслуживания'
        verbose_name_plural = 'Интервалы обслуживания'


class Place(BaseName, Base):
    """Место обслуживания"""
    __tablename__ = "place"

    si: Mapped["Si"] = relationship(back_populates="place")

    class Meta(BaseName.Meta):
        verbose_name = 'Место обслуживания'
        verbose_name_plural = 'Места обслуживания'


class Room(BaseName, Base):
    """№ помещения"""
    __tablename__ = "room"

    class Meta(BaseName.Meta):
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'


class DescriptionMethod(BaseName, Base):
    """Описание СИ и методика поверки СИ"""
    __tablename__ = "description_method"

    description: Mapped[Optional[str]] = mapped_column(
        info={'label': 'Описание СИ'})
    method: Mapped[Optional[str]] = mapped_column(
        info={'label': 'Методика поверки СИ'})

    si: Mapped["Si"] = relationship(back_populates="description_method")

    class Meta(BaseName.Meta):
        verbose_name = 'Описание и методика поверки СИ'
        verbose_name_plural = 'Описания и методики поверки СИ'
        verbose_name_change = 'Описание и методику поверки СИ'


class Division(BaseName, Base):
    """Подразделение"""
    __tablename__ = "division"

    employee: Mapped["Employee"] = relationship(back_populates="division")

    class Meta(BaseName.Meta):
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'


class Employee(BasePK, Base):
    """Ответственное лицо (сотрудник)"""
    __tablename__ = "employee"

    last_name: Mapped[Optional[str_100]] = mapped_column(
        info={'label': 'Фамилия'})
    first_name: Mapped[str_100] = mapped_column(
        info={'label': 'Имя'})
    middle_name: Mapped[Optional[str_100]] = mapped_column(
        info={'label': 'Отчество'})
    email: Mapped[Optional[str]] = mapped_column(
        info={'label': 'e-mail'}, unique=True)
    division_id: Mapped[int] = mapped_column(
        ForeignKey("division.id", ondelete="CASCADE"),
        info={'label': 'Подразделение'},
    )

    division: Mapped["Division"] = relationship(back_populates="employee")
    si: Mapped["Si"] = relationship(back_populates="employee")

    class Meta:
        verbose_name = 'Ответственное лицо'
        verbose_name_plural = 'Ответственные лица'
        select_related = ['division']
        fields_display = ['__str__', 'email', 'division']
        ordering = ('last_name', 'first_name', 'middle_name')

    def get_full_name(self):
        # Формирование полного имени "Фамилия Имя Отчество"
        try:
            full_name = "%s %s %s" % (str(self.last_name.capitalize()),
                                      str(self.first_name.capitalize()),
                                      str(self.middle_name.capitalize())
                                      )
        except AttributeError:
            return str(self.last_name).capitalize()

        return full_name.strip()

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

    def __str__(self):
        return self.get_full_name()
