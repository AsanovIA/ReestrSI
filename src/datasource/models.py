import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base, BasePK, str_100, str_256


class BaseName(BasePK):
    name: Mapped[str_256] = mapped_column(unique=True)

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
    """Межповерочный интервал"""
    __tablename__ = "service_interval"

    name: Mapped[int]

    si: Mapped["Si"] = relationship(back_populates="service_interval")

    class Meta(BaseName.Meta):
        verbose_name = 'Межповерочный интервал'
        verbose_name_plural = 'Межповерочные интервалы'


class Place(BaseName, Base):
    """Место поверки/калибровки"""
    __tablename__ = "place"

    si: Mapped["Si"] = relationship(back_populates="place")

    class Meta(BaseName.Meta):
        verbose_name = 'Место поверки/калибровки'
        verbose_name_plural = 'Места поверки/калибровки'


class Room(BaseName, Base):
    """№ помещения"""
    __tablename__ = "room"

    class Meta(BaseName.Meta):
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'


class DescriptionMethod(BaseName, Base):
    """Описание СИ и методика поверки СИ"""
    __tablename__ = "description_method"

    description: Mapped[Optional[str]]
    method: Mapped[Optional[str]]

    si: Mapped["Si"] = relationship(back_populates="description_method")

    class Meta(BaseName.Meta):
        verbose_name = 'Описание и методика поверки СИ'
        verbose_name_plural = 'Описания и методики поверки СИ'


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

    last_name: Mapped[Optional[str_100]]
    first_name: Mapped[str_100]
    middle_name: Mapped[Optional[str_100]]
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    division_id: Mapped[int] = mapped_column(
        ForeignKey("division.id", ondelete="CASCADE")
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


class Si(BasePK, Base):
    """Средство измерения"""
    __tablename__ = "si"

    group_si_id: Mapped[int] = mapped_column(
        ForeignKey("group_si.id", ondelete="CASCADE")
    )
    name_si_id: Mapped[int] = mapped_column(
        ForeignKey("name_si.id", ondelete="CASCADE")
    )
    type_si_id: Mapped[int] = mapped_column(
        ForeignKey("type_si.id", ondelete="CASCADE")
    )
    number: Mapped[str]
    description_method_id: Mapped[int] = mapped_column(
        ForeignKey("description_method.id", ondelete="CASCADE")
    )
    service_type_id: Mapped[int] = mapped_column(
        ForeignKey("service_type.id", ondelete="CASCADE")
    )
    service_interval_id: Mapped[int] = mapped_column(
        ForeignKey("service_interval.id", ondelete="CASCADE")
    )
    etalon: Mapped[bool]
    category_etalon: Mapped[Optional[str]]
    year_production: Mapped[Optional[int]] = mapped_column(
        info={'check': 'LENGTH(year_production) = 4'},
    )
    nomenclature: Mapped[Optional[str_256]]
    place_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("place.id", ondelete="CASCADE"),
    )
    control_vp: Mapped[bool]
    room_use_etalon_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("room.id", ondelete="CASCADE"),
    )
    room_delivery_id: Mapped[int] = mapped_column(
        ForeignKey("room.id", ondelete="CASCADE")
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employee.id", ondelete="CASCADE")
    )
    date_last_service: Mapped[Optional[datetime.date]]
    date_next_service: Mapped[datetime.date]
    certificate: Mapped[Optional[str]]
    is_service: Mapped[bool] = mapped_column(default=False)

    group_si: Mapped["GroupSi"] = relationship(back_populates="si")
    name_si: Mapped["NameSi"] = relationship(back_populates="si")
    type_si: Mapped["TypeSi"] = relationship(back_populates="si")
    service_type: Mapped["ServiceType"] = relationship(back_populates="si")
    service_interval: Mapped["ServiceInterval"] = relationship(
        back_populates="si"
    )
    description_method: Mapped["DescriptionMethod"] = relationship(
        back_populates="si"
    )
    place: Mapped["Place"] = relationship(back_populates="si")
    room_use_etalon: Mapped["Room"] = relationship(
        foreign_keys=[room_use_etalon_id],
    )
    room_delivery: Mapped["Room"] = relationship(
        foreign_keys=[room_delivery_id],
    )
    employee: Mapped["Employee"] = relationship(back_populates="si")

    class Meta:
        verbose_name = 'Средство измерения'
        verbose_name_plural = 'Средства измерения'
        select_related = [
            'group_si',
            'name_si',
            'type_si',
            'service_type',
            'service_interval',
            'description_method',
            'place',
            'room_use_etalon',
            'room_delivery',
            'employee',
        ]
        fields_display = [
            'group_si',
            'name_si',
            'type_si',
            'number',
            'description_method',
            'service_type',
            'service_interval',
            'etalon',
            'category_etalon',
            'year_production',
            'nomenclature',
            'room_use_etalon',
            'place',
            'control_vp',
            'room_delivery',
            'employee',
            'date_last_service',
            'date_next_service',
            'certificate',
            'is_service',
        ]

    def __str__(self):
        return self.number
