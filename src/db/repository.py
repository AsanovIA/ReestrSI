from collections.abc import Iterable
from flask import g
from sqlalchemy import select, insert, desc
from sqlalchemy.orm import joinedload
from typing import Union

from src.db.database import Base, engine, session_factory


def get_options_load(model):
    def get_related_model():
        try:
            select_related = model.Meta.select_related
        except AttributeError:
            return

        for field_name in select_related:
            try:
                field = getattr(model, field_name)
            except AttributeError:
                lookup_fields = field_name.split("__")
                lookup_model = model
                for index, path_part in enumerate(lookup_fields):
                    field = getattr(lookup_model, path_part)
                    lookup_model = field.property.entity.class_
                    if index == 0:
                        join_load = joinedload(field)
                    else:
                        join_load = join_load.joinedload(field)
            else:
                join_load = joinedload(field)

            yield join_load

    return list(get_related_model())


class Repository:

    @classmethod
    def recreate_table(cls):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    @classmethod
    def bulk_insert(cls, model, values):
        with session_factory() as session:
            count = session.query(model).count()
            if count == 0:
                session.execute(insert(model), values)
                session.commit()

    @classmethod
    def task_count(cls, q):
        model = q.model
        filters = q.filters
        with session_factory() as session:
            query = session.query(model)
            if filters:
                query = query.filter(*filters)
            result = query.count()

        return result

    @classmethod
    def task_exists(cls, filters, model=None):
        model = model or g.model
        with session_factory() as session:
            subq = session.query(model).filter(*filters)
            result = session.query(subq.exists()).scalar()

        return result

    @classmethod
    def task_get_list(cls, q):
        model = q.model
        filters = q.filters
        joins = q.joins
        ordering = q.ordering
        limit = q.limit
        offset = q.offset

        with session_factory() as session:
            query = select(model).select_from(model)

            if joins and isinstance(joins, Iterable):
                for j in joins:
                    query = query.join(j)
            if filters and isinstance(filters, Iterable):
                query = query.filter(*filters)
            if ordering:
                query = query.order_by(*ordering)
            options_load = get_options_load(model)
            query = query.options(*options_load)
            if limit:
                query = query.offset(offset).limit(limit)

            result_query = session.execute(query)
            result = result_query.unique().scalars().all()

        return result

    @classmethod
    def task_get_object(cls, filters: Union[dict, str, int], model=None):
        model = model or g.model

        if (isinstance(filters, int)
                or isinstance(filters, str) and filters.isdigit()):
            filters = {'id': int(filters)}
        elif not isinstance(filters, dict):
            raise ValueError(
                f'{filters} должен быть int, "int", dict'
            )

        with session_factory() as session:
            query = select(model).filter_by(**filters)

            options_load = get_options_load(model)
            query = query.options(*options_load)

            result = session.execute(query).scalar_one()

        return result

    @classmethod
    def task_update_object(cls, obj):
        with session_factory() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)

    @classmethod
    def task_add_object(cls, obj):
        with session_factory() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            g.object = obj

    @classmethod
    def task_add_si_and_service(cls, obj):
        with session_factory() as session:
            session.add(obj)
            session.flush()
            g.object_service.si_id = obj.id
            session.add(g.object_service)
            session.commit()
            session.refresh(obj)
            g.object = obj

    @classmethod
    def task_update_si_and_service(cls, obj, service=None):
        with session_factory() as session:
            if service:
                object_service = (
                    session
                    .query(service)
                    .filter(service.si_id == obj.id)
                    .order_by(desc(service.id))
                    .first()
                )
                object_service.date_last_service = obj.date_last_service
                object_service.date_next_service = obj.date_next_service
                object_service.certificate = obj.certificate

            session.add(obj)
            session.commit()
            session.refresh(obj)

    @classmethod
    def task_add_and_out_service(cls, obj):
        if not isinstance(obj, (list, tuple)):
            obj = [obj, g.object_si]
        with session_factory() as session:
            session.add_all(obj)
            session.commit()
            session.refresh(g.object_si)

    @classmethod
    def task_delete_object(cls, obj):
        with session_factory() as session:
            session.delete(obj)
            session.commit()
