from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base, BasePK, str_100, str_256


class BaseView(BasePK):
    view: Mapped[bool] = mapped_column(
        info={'label': 'Отображение'},
        default=True
    )


class BaseViewName(BaseView):
    name: Mapped[str_256] = mapped_column(
        info={'label': 'Наименование'}, unique=True)

    class Meta:
        ordering = ('name',)
        fields_display = ('name',)
        fields_search = ('name',)

    def __str__(self):
        return str(self.name)


class GroupSi(BaseViewName, Base):
    """Группы СИ по областям и разделам областей измерений"""
    __tablename__ = "group_si"

    si: Mapped["Si"] = relationship(back_populates="group_si")

    class Meta(BaseViewName.Meta, Base.Meta):
        action_suffix = 'а'
        verbose_name = 'Группа СИ по областям и разделам областей измерений'
        verbose_name_plural = (
            'Группы СИ по областям и разделам областей измерений'
        )
        verbose_name_change = (
            'Группу СИ по областям и разделам областей измерений'
        )


class NameSi(BaseViewName, Base):
    """Наименование СИ"""
    __tablename__ = "name_si"

    si: Mapped["Si"] = relationship(back_populates="name_si")

    class Meta(BaseViewName.Meta, Base.Meta):
        action_suffix = 'о'
        verbose_name = 'Наименование СИ'
        verbose_name_plural = 'Наименования СИ'


class TypeSi(BaseViewName, Base):
    """Тип СИ"""
    __tablename__ = "type_si"

    si: Mapped["Si"] = relationship(back_populates="type_si")

    class Meta(BaseViewName.Meta, Base.Meta):
        verbose_name = 'Тип СИ'
        verbose_name_plural = 'Типы СИ'


class ServiceType(BaseViewName, Base):
    """Вид метрологического обслуживания"""
    __tablename__ = "service_type"

    si: Mapped["Si"] = relationship(back_populates="service_type")

    class Meta(BaseViewName.Meta, Base.Meta):
        verbose_name = 'Вид метрологического обслуживания'
        verbose_name_plural = 'Виды метрологического обслуживания'


class ServiceInterval(BaseViewName, Base):
    """Интервал обслуживания"""
    __tablename__ = "service_interval"

    name: Mapped[int]

    si: Mapped["Si"] = relationship(back_populates="service_interval")

    class Meta(BaseViewName.Meta, Base.Meta):
        verbose_name = 'Интервал обслуживания'
        verbose_name_plural = 'Интервалы обслуживания'


class Place(BaseViewName, Base):
    """Место обслуживания"""
    __tablename__ = "place"

    si: Mapped["Si"] = relationship(back_populates="place")

    class Meta(BaseViewName.Meta, Base.Meta):
        action_suffix = 'о'
        verbose_name = 'Место обслуживания'
        verbose_name_plural = 'Места обслуживания'


class Room(BaseViewName, Base):
    """№ помещения"""
    __tablename__ = "room"

    class Meta(BaseViewName.Meta, Base.Meta):
        action_suffix = 'о'
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'


class StatusService(BaseViewName, Base):
    """Состояние обслуживания СИ"""
    __tablename__ = "status_service"

    si: Mapped["Si"] = relationship(back_populates="status_service")
    service: Mapped["Service"] = relationship(back_populates="status_service")

    class Meta(BaseViewName.Meta, Base.Meta):
        action_suffix = 'о'
        verbose_name = 'Состояние обслуживания СИ'
        verbose_name_plural = 'Состояния обслуживания СИ'


class DescriptionMethod(BaseViewName, Base):
    """Описание СИ и методика поверки СИ"""
    __tablename__ = "description_method"

    description: Mapped[Optional[str]] = mapped_column(
        info={
            'label': 'Описание типа СИ',
            'type': 'FileField',
            'upload': 'description/',
        })
    description_hash: Mapped[Optional[str]]
    method: Mapped[Optional[str]] = mapped_column(
        info={
            'label': 'Методика поверки СИ',
            'type': 'FileField',
            'upload': 'method/',
        })
    method_hash: Mapped[Optional[str]]

    si: Mapped["Si"] = relationship(back_populates="description_method")

    class Meta(BaseViewName.Meta, Base.Meta):
        action_suffix = 'ы'
        verbose_name = 'Описание типа и методика поверки СИ'
        verbose_name_plural = 'Описания типа и методики поверки СИ'
        verbose_name_change = 'Описание типа и методику поверки СИ'
        fields_display = ('name', 'description', 'method')


class Division(BaseViewName, Base):
    """Подразделение"""
    __tablename__ = "division"

    employee: Mapped["Employee"] = relationship(back_populates="division")

    class Meta(BaseViewName.Meta, Base.Meta):
        action_suffix = 'о'
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'


class Employee(BaseView, Base):
    """Ответственное лицо (сотрудник)"""
    __tablename__ = "employee"

    last_name: Mapped[str_100] = mapped_column(
        info={'label': 'Фамилия'})
    first_name: Mapped[Optional[str_100]] = mapped_column(
        info={'label': 'Имя'})
    middle_name: Mapped[Optional[str_100]] = mapped_column(
        info={'label': 'Отчество'})
    email: Mapped[Optional[str]] = mapped_column(
        info={'label': 'e-mail'}, unique=True)
    division_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("division.id", ondelete="CASCADE"),
        info={'label': 'Подразделение'},
    )

    division: Mapped["Division"] = relationship(back_populates="employee")
    si: Mapped["Si"] = relationship(back_populates="employee")

    class Meta(Base.Meta):
        action_suffix = 'о'
        verbose_name = 'Ответственное лицо'
        verbose_name_plural = 'Ответственные лица'
        ordering = ('last_name', 'first_name', 'middle_name')
        select_related = ('division',)
        fields_display = ('__str__', 'email', 'division')
        fields_search = (
            'last_name', 'first_name', 'middle_name', 'division__name'
        )

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
