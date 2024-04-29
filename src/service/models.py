import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.database import Base, BasePK


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
    nomenclature: Mapped[Optional[str]]
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

    service: Mapped["Service"] = relationship(back_populates="si")

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


class Service(BasePK, Base):
    """Сервис - обслуживание средств измерения"""
    __tablename__ = "service"

    si_id: Mapped[int] = mapped_column(
        ForeignKey("si.id", ondelete="CASCADE")
    )
    date_in_service: Mapped[datetime.date]
    date_out_service: Mapped[Optional[datetime.date]]
    date_last_service: Mapped[Optional[datetime.date]]
    date_next_service: Mapped[Optional[datetime.date]]
    certificate: Mapped[Optional[str]]
    note: Mapped[Optional[str]]
    is_ready: Mapped[bool] = mapped_column(default=False)
    is_out: Mapped[bool] = mapped_column(default=False)

    si: Mapped["Si"] = relationship(
        doc='Средство измерения',
        back_populates="service"
    )

    class Meta:
        verbose_name = 'Обслуживание СИ'
        verbose_name_plural = 'Обслуживание СИ'
        select_related = ['si']
        fields_display = [
            'si', 'date_in_service', 'date_last_service', 'is_ready',
            'date_next_service', 'certificate', 'note'
        ]
