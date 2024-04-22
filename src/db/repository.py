from flask import g
from collections.abc import Iterable
from typing import Union

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import joinedload

from src.db.database import Base, engine, session_factory


def _get_options_load(model):
    def get_related_model():
        try:
            select_related = model.Meta.select_related
        except AttributeError:
            select_related = []
        for rel in select_related:
            yield joinedload(getattr(model, rel))

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
    def task_get_list(
            cls,
            model=None,
            filters: Union[list, tuple, None] = None,
            **kwargs,
    ):
        model = model or g.model

        with session_factory() as session:
            query = select(model)
            if filters and isinstance(filters, Iterable):
                query = select(model).filter(*filters)
            options_load = _get_options_load(model)
            query = query.options(*options_load)
            result_query = session.execute(query)
            result = result_query.unique().scalars().all()

        return result

    @classmethod
    def task_get_object(
            cls,
            filters: Union[dict, str, int],
            model=None,
    ):
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
            options_load = _get_options_load(model)
            query = query.options(*options_load)
            result = session.execute(query).scalar_one()

        return result

    @classmethod
    def task_add_or_update_object(cls, obj):
        if not isinstance(obj, (list, tuple)):
            obj = [obj]
        with session_factory() as session:
            session.add_all(obj)
            session.commit()

    @classmethod
    def task_delete_object(cls, pk):
        with session_factory() as session:
            query = delete(g.model).filter_by(id=pk)
            session.execute(query)
            session.commit()
