import datetime

from flask import g
from sqlalchemy import Boolean, desc, or_
from sqlalchemy.orm import Relationship
from typing import Union, List, Tuple

from src.core.constants import ALL_VAR, FILTER_SUFFIX, LOOKUP_SEP, SEARCH_VAR
from src.core.exceptions import ModelDoesNotExist
from src.core.utils import convert_quoted_string


class Query:
    def __init__(
            self,
            model=None,
            params=None,
            fields_filter: Union[List[str], Tuple[str], None] = None,
            fields_search: Union[List[str], Tuple[str], None] = None,
            ordering: Union[List[str], Tuple[str], None] = None,
            filters: Union[list, tuple, None] = None,
            joins: Union[list, None] = None,
            limit: int = None,
            offset: int = 0,
    ):
        self.model = model or getattr(g, 'model', None)
        if self.model is None:
            raise ModelDoesNotExist('Не найдена модель для запроса')
        self.fields_filter = [] if fields_filter is None else fields_filter
        self.fields_search = [] if fields_search is None else fields_search
        self.ordering = self.get_ordering(ordering)
        self.limit = limit
        self.offset = offset
        self.filters = list(filters) if filters else []
        self.joins = set(joins) if joins else set()
        if params:
            self.params = dict(params)
            self.construct_query()

    def get_ordering(self, fields=None):
        if fields is None:
            try:
                fields = getattr(g, 'ordering')
            except AttributeError:
                fields = getattr(self.model.Meta, 'ordering', [])

        def create_ordering():
            for field in fields:
                asc_desc = True
                if field.startswith("-"):
                    asc_desc = False
                    field = field[1:]
                if not hasattr(self.model, field):
                    continue
                if asc_desc:
                    yield getattr(self.model, field)
                else:
                    yield desc(getattr(self.model, field))

        return list(create_ordering())

    def __add__(self, other):
        combined = Query()
        combined.model = self.model
        combined.fields_filter = self.fields_filter[:]
        combined.fields_search = self.fields_search[:]
        combined.ordering = self.ordering[:]
        combined.limit = self.limit
        combined.offset = self.offset
        combined.filters = self.filters[:]
        combined.joins = self.joins.union(other.joins)
        for item in other.filters:
            if item not in self.filters:
                combined.filters.append(item)
        return combined

    def construct_query(self):
        for param, value in self.params.items():
            if param == SEARCH_VAR and len(value) > 2:
                self.query_search(value)

            elif FILTER_SUFFIX in param and value != ALL_VAR:
                filter_name = param.rsplit(LOOKUP_SEP, maxsplit=1)[0]
                if any(
                        filter_name.endswith(s)
                        for s in [LOOKUP_SEP + 'begin', LOOKUP_SEP + 'end']
                ):
                    if not value:
                        continue
                    self.query_filter_date(filter_name, value)
                else:
                    self.query_filter_related(filter_name, value)

    def lookup_field_related(self, model, field_name):
        if LOOKUP_SEP in field_name:
            lookup_fields = field_name.split(LOOKUP_SEP)
            for index, path_part in enumerate(lookup_fields):
                field_name = path_part
                field = getattr(model, path_part)
                if (
                        isinstance(field.property, Relationship)
                        and index < len(lookup_fields) - 1
                ):
                    model = field.property.entity.class_
                    self.joins.add(field)

        return model, field_name

    def query_filter_related(self, field_name, value):
        model = self.model
        model, field_name = self.lookup_field_related(model, field_name)

        try:
            field = getattr(model, field_name + '_id')
            if value:
                filter_ = field == int(value)
            else:
                filter_ = field.is_(None)
        except AttributeError:
            field = getattr(self.model, field_name)
            if isinstance(field.type, Boolean):
                filter_ = field == int(value)
            else:
                return

        self.filters.append(filter_)

    def query_filter_date(self, name, value):
        name = name.rsplit(LOOKUP_SEP, maxsplit=1)
        model, field_name = self.lookup_field_related(self.model, name[0])
        field = getattr(model, field_name)
        value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        if name[-1] == 'begin':
            filter_ = field >= value
        else:
            filter_ = field <= value

        self.filters.append(filter_)

    def query_search(self, value: str):
        values = [
            convert_quoted_string(s)
            if s.startswith(('"', "'")) and s[0] == s[-1] else s
            for s in value.split(' ')
        ]
        for value in values:
            or_queries = []
            for field_name in self.fields_search:
                model = self.model
                lookup_fields = field_name.split(LOOKUP_SEP)
                for path_part in lookup_fields:
                    field = getattr(model, path_part)
                    if isinstance(field.property, Relationship):
                        model = field.property.entity.class_
                        self.joins.add(field)
                        continue
                    or_queries.append(field.ilike(f'%{value}%'))

            self.filters.append(or_(*or_queries))
