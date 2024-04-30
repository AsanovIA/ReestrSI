from collections.abc import Iterable
from flask import g
from sqlalchemy import select, insert, delete, desc
from sqlalchemy.orm import joinedload
from typing import Union

from src.db.database import Base, engine, session_factory


def get_options_load(model, related=None):
    def get_related_model():
        try:
            select_related = model.Meta.select_related
        except AttributeError:
            return

        for field_name in select_related:
            if '.' in field_name:
                if related is None:
                    raise TypeError('Не определены зависимые модели')
                fields_related = field_name.split('.')
                if len(fields_related) == 3:
                    try:
                        model_related1 = related[fields_related[0]]
                        model_related2 = related[fields_related[1]]
                    except KeyError as e:
                        raise KeyError(f'Не получен ожидаемый ключ {e}')
                    yield joinedload(
                        getattr(model, fields_related[0])
                    ).joinedload(
                        getattr(model_related1, fields_related[1])
                    ).joinedload(
                        getattr(model_related2, fields_related[2])
                    )

                elif len(fields_related) == 2:
                    try:
                        model_related = related[fields_related[0]]
                    except KeyError as e:
                        raise KeyError(f'Не получен ожидаемый ключ {e}')
                    yield joinedload(
                        getattr(model, fields_related[0])
                    ).joinedload(getattr(model_related, fields_related[1]))

                else:
                    raise ('Программно не прописано получение более тройной '
                           'зависимости')
            else:
                yield joinedload(getattr(model, field_name))

    return list(get_related_model())


def get_ordering(model):
    try:
        fields = getattr(model.Meta, 'ordering')
    except AttributeError:
        return ()

    def create_ordering():
        for field in fields:
            asc_desc = True
            if field.startswith("-"):
                asc_desc = False
                field = field[1:]
            if not hasattr(model, field):
                continue
            if asc_desc:
                yield getattr(model, field)
            else:
                yield desc(getattr(model, field))

    return tuple(create_ordering())


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
    def task_count(cls, model=None):
        model = model or g.model
        with session_factory() as session:
            result = session.query(model).count()

        return result

    @classmethod
    def task_exists(cls, filters, model=None):
        model = model or g.model
        with session_factory() as session:
            subq = session.query(model).filter(*filters)
            result = session.query(subq.exists()).scalar()

        return result

    @classmethod
    def task_get_list(
            cls,
            model=None,
            model_related=None,
            filters: Union[list, tuple, None] = None,
            ordering: tuple = (),
            limit: int = 20,
            offset: int = 0,
            **kwargs,
    ):
        model = model or g.model
        ordering = ordering or get_ordering(model)

        with session_factory() as session:
            query = select(model)
            if filters and isinstance(filters, Iterable):
                query = select(model).filter(*filters)
            if ordering:
                query = query.order_by(*ordering)

            options_load = get_options_load(model, related=model_related)
            query = query.options(*options_load)

            query = query.offset(offset).limit(limit)
            result_query = session.execute(query)
            result = result_query.unique().scalars().all()

        return result

    @classmethod
    def task_get_object(
            cls,
            filters: Union[dict, str, int],
            model=None,
            related_model=None,
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

            options_load = get_options_load(model, related_model)
            query = query.options(*options_load)

            result = session.execute(query).scalar_one()

        return result

    @classmethod
    def task_update_object(cls, obj):
        with session_factory() as session:
            session.add(obj)
            session.commit()

    @classmethod
    def task_add_object(cls, obj):
        with session_factory() as session:
            session.add(obj)
            session.flush()
            session.commit()
            g.object_id = obj.id

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
