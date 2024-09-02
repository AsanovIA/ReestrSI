from collections.abc import Iterable
from flask import g
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload, selectinload
from typing import Union

from src.db.database import Base, engine, session_factory


def get_options_load(model):
    def generate_options():
        def related_model(field_name, func_load):
            try:
                field = getattr(model, field_name)
            except AttributeError:
                lookup_fields = field_name.split("__")
                lookup_model = model
                for index, path_part in enumerate(lookup_fields):
                    field = getattr(lookup_model, path_part)
                    lookup_model = field.property.entity.class_
                    if index == 0:
                        result_load = func_load(field)
                    else:
                        attr = getattr(result_load, func_load.__name__)
                        result_load = attr(field)
            else:
                result_load = func_load(field)

            return result_load

        try:
            joined_related = model.Meta.joined_related
        except AttributeError:
            joined_related = None
        try:
            select_in_related = model.Meta.select_in_related
        except AttributeError:
            select_in_related = None

        if not joined_related and not select_in_related:
            return

        if joined_related:
            for field_name in joined_related:
                yield related_model(field_name, joinedload)
        if select_in_related:
            for field_name in select_in_related:
                yield related_model(field_name, selectinload)

    return list(generate_options())


class Repository:

    @classmethod
    def recreate_table(cls):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    @classmethod
    def bulk_insert(cls, model, values):
        with session_factory() as session:
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
    def task_get_list(cls, q, first=None):
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
            if first:
                result = result_query.scalars().first()
            else:
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

            result = session.execute(query).unique().scalar_one()

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
    def task_add_si(cls, obj):
        with session_factory() as session:
            session.add(obj)
            session.flush()
            g.object_service.si_id = obj.id
            session.add(g.object_service)
            session.commit()
            session.refresh(obj)
            g.object = obj

    @classmethod
    def task_out_service(cls, obj):
        objs = [obj, g.object_si]
        with session_factory() as session:
            session.add_all(objs)
            session.commit()
            session.refresh(obj)

    @classmethod
    def task_update_service(cls, obj, status):
        with session_factory() as session:
            obj = session.merge(obj)
            g.object_si = session.merge(g.object_si)
            object_status = (
                session
                .query(status)
                .filter(status.id == obj.status_service_id)
                .one()
            )
            g.object_si.status_service = object_status.name
            session.commit()
            session.refresh(g.object_si)

    @classmethod
    def task_add_service(cls, obj):
        with session_factory() as session:
            objs = [obj, g.object_si]
            session.add_all(objs)
            session.flush()
            g.object_si.status_service = obj.status_service.name
            session.commit()
            session.refresh(g.object_si)

    @classmethod
    def task_delete_object(cls, obj):
        with session_factory() as session:
            session.delete(obj)
            session.commit()
