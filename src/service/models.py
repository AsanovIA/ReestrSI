import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.database import Base, BasePK
from src.core.utils import value_for_field


class Si(BasePK, Base):
    """Средство измерения"""
    __tablename__ = "si"

    group_si_id: Mapped[int] = mapped_column(
        ForeignKey("group_si.id", ondelete="CASCADE"),
        info={'label': 'Группы СИ по областям и разделам областей измерений'}
    )
    name_si_id: Mapped[int] = mapped_column(
        ForeignKey("name_si.id", ondelete="CASCADE"),
        info={'label': 'Наименование СИ'}
    )
    type_si_id: Mapped[int] = mapped_column(
        ForeignKey("type_si.id", ondelete="CASCADE"),
        info={'label': 'Тип СИ'}
    )
    number: Mapped[str] = mapped_column(info={'label': 'Заводской номер'})
    description_method_id: Mapped[int] = mapped_column(
        ForeignKey("description_method.id", ondelete="CASCADE"),
        info={'label': 'Описание и методика поверки СИ'}
    )
    service_type_id: Mapped[int] = mapped_column(
        ForeignKey("service_type.id", ondelete="CASCADE"),
        info={'label': 'Вид метрологического обслуживания'}
    )
    service_interval_id: Mapped[int] = mapped_column(
        ForeignKey("service_interval.id", ondelete="CASCADE"),
        info={'label': 'Интервал обслуживания'}
    )
    etalon: Mapped[bool] = mapped_column(info={'label': 'Эталон'})
    category_etalon: Mapped[Optional[str]] = mapped_column(
        info={'label': 'Категория эталона'})
    year_production: Mapped[Optional[int]] = mapped_column(
        info={
            'check': 'LENGTH(year_production) = 4',
            'label': 'Год производства',
        },
    )
    nomenclature: Mapped[Optional[str]] = mapped_column(
        info={'label': 'Номенклатурный номер'})
    place_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("place.id", ondelete="CASCADE"),
        info={'label': 'Место обслуживания'}
    )
    control_vp: Mapped[bool] = mapped_column(info={'label': 'Контроль ВП'})
    room_use_etalon_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("room.id", ondelete="CASCADE"),
        info={'label': '№ помещения, в котором применяется эталон'}
    )
    room_delivery_id: Mapped[int] = mapped_column(
        ForeignKey("room.id", ondelete="CASCADE"),
        info={'label': '№ помещения где можно получить СИ после обслуживания'}
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employee.id", ondelete="CASCADE"),
        info={'label': 'Ответственное лицо'}
    )
    date_last_service: Mapped[Optional[datetime.date]] = mapped_column(
        info={'label': 'Дата последнего обслуживания'})
    date_next_service: Mapped[datetime.date] = mapped_column(
        info={'label': 'Дата следующего обслуживания'})
    certificate: Mapped[Optional[str]] = mapped_column(
        info={
            'label': 'Сертификат',
            'type': 'FileField',
            'upload': 'certificate/',
        })
    is_service: Mapped[bool] = mapped_column(
        info={'label': 'На обслуживании'}, default=False)

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

    service: Mapped["Service"] = relationship(back_populates="si")

    class Meta(Base.Meta):
        action_suffix = 'о'
        verbose_name = 'Средство измерения'
        verbose_name_plural = 'Средства измерения'

        select_related = (
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
            'employee__division',
        )
        fields_display = (
            'group_si',
            'name_si',
            'type_si',
            'number',
            'description_method',
            'description',
            'method',
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
            'division',
            'email',
            'date_last_service',
            'date_next_service',
            'certificate',
            'is_service',
        )
        fields_filter = (
            'group_si',
            'name_si',
            'type_si',
            'description_method',
            'service_type',
            'service_interval',
            'etalon',
            'room_use_etalon',
            'place',
            'control_vp',
            'room_delivery',
            'employee',
            'employee__division',
            'date_last_service',
            'date_next_service',
            'is_service',
        )
        fields_search = (
            'group_si__name',
            'name_si__name',
            'type_si__name',
            'number',
            'description_method__name',
            # 'service_type__name',
            # 'service_interval__name',
            'category_etalon',
            'year_production',
            'nomenclature',
            # 'room_use_etalon__name',
            # 'place__name',
            # 'room_delivery__name',
            # 'employee__last_name',
            # 'employee__first_name',
            # 'employee__middle_name',
            # 'employee__division__name',
        )

    def __str__(self):
        return self.number

    def division(self):
        return self.employee.division

    def email(self):
        return self.employee.email

    def description(self):
        return value_for_field('description_method__description', self)

    def method(self):
        return value_for_field('description_method__method', self)

    division.short_description = 'Подразделение'
    email.short_description = 'e-mail'
    description.short_description = 'Описание СИ'
    method.short_description = 'Методика поверки СИ'


class Service(BasePK, Base):
    """Сервис - обслуживание средств измерения"""
    __tablename__ = "service"

    si_id: Mapped[int] = mapped_column(
        ForeignKey("si.id", ondelete="CASCADE"),
        info={'label': 'Средство измерения'}
    )
    date_in_service: Mapped[datetime.date] = mapped_column(
        info={'label': 'Дата поступления на обслуживание'})
    date_out_service: Mapped[Optional[datetime.date]] = mapped_column(
        info={'label': 'Дата возврата с обслуживания'})
    date_last_service: Mapped[Optional[datetime.date]] = mapped_column(
        info={'label': 'Дата последнего обслуживания'})
    date_next_service: Mapped[Optional[datetime.date]] = mapped_column(
        info={'label': 'Дата следующего обслуживания'})
    certificate: Mapped[Optional[str]] = mapped_column(
        info={
            'label': 'Сертификат',
            'type': 'FileField',
            'upload': 'certificate/',
        })
    note: Mapped[Optional[str]] = mapped_column(info={'label': 'Примечание'})
    is_ready: Mapped[bool] = mapped_column(
        info={'label': 'Готовность к выдачи'}, default=False)
    is_out: Mapped[bool] = mapped_column(
        info={'label': 'Выдан'}, default=False)

    si: Mapped["Si"] = relationship(back_populates="service")

    class Meta(Base.Meta):
        action_suffix = 'о'
        verbose_name = 'Обслуживание СИ'
        verbose_name_plural = 'Обслуживание СИ'
        ordering = ('date_in_service',)
        select_related = ('si',)
        fields_display = (
            'si', 'date_in_service', 'date_last_service', 'is_ready',
            'date_next_service', 'certificate', 'note'
        )
        fields_filter = ('is_ready',)
        fields_search = ('si__number',)

    def __str__(self):
        return str(self.si)
