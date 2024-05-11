from flask import g, request
from sqlalchemy import Boolean, Date
from sqlalchemy.orm import Relationship, InstrumentedAttribute

from src.core.exceptions import FieldDoesNotExist
from src.core.fields import FilterSelectField, FilterDateField
from src.core.utils import label_for_field, get_model


class FilterForm:
    def __init__(self):
        self.filters = []
        relation_filters, boolean_filters, date_filters = [], [], []
        model = g.model
        for field_name in g.fields_filter:
            if field_name not in g.fields_display:
                continue

            field = getattr(model, field_name)
            if not isinstance(field, InstrumentedAttribute):
                if hasattr(field, 'path_related'):
                    names = field.path_related.split('.')
                    related_model = get_model(names[-2])
                    field = getattr(related_model, names[-1])
                else:
                    raise FieldDoesNotExist(
                        f'Невозможно определить фильтр для {field.__name__}'
                    )

            if isinstance(field.property, Relationship):
                filter_ = RelatedListFilter(field_name, field)
                relation_filters.append(filter_)
            elif isinstance(field.type, Boolean):
                filter_ = BooleanListFilter(field_name)
                boolean_filters.append(filter_)
            elif isinstance(field.type, Date):
                filter_ = DateListFilter(field_name)
                date_filters.append(filter_)
            else:
                raise Exception(f'Фильтра для {field.key} нет')

        self.filters = relation_filters + boolean_filters + date_filters

    def __iter__(self):
        return iter(self.filters)


class ListFilter:
    field = None

    def __init__(self, field_name):
        self.title = label_for_field(field_name)
        name = '%s__exact' % field_name
        id = '%s__id' % field_name
        data = request.args.get(name)
        self.options = {
            'name': name,
            'id': id,
            'data': data,
        }

    def __str__(self):
        return self.field()

    def __html__(self):
        return self.field()


class RelatedListFilter(ListFilter):
    def __init__(self, field_name, field):
        super().__init__(field_name)
        self.type = 'select'
        self.options.update(model=field.property.argument)
        self.field = FilterSelectField(**self.options)


class BooleanListFilter(ListFilter):
    def __init__(self, field_name):
        super().__init__(field_name)
        self.type = 'boolean'
        choices = [('1', 'Да'), ('0', 'Нет')]
        self.options.update(choices=choices)
        self.field = FilterSelectField(**self.options)


class DateListFilter(ListFilter):
    def __init__(self, field_name):
        super().__init__(field_name)
        self.type = 'date'
        self.fields = []
        for suffix in ['__begin', '__end']:
            field_name_suffix = field_name + suffix
            name = '%s__exact' % field_name_suffix
            id = '%s__id' % field_name_suffix
            data = request.args.get(name, '')
            self.options.update({
                'name': name,
                'id': id,
                'data': data
            })
            field = FilterDateField(**self.options)
            self.fields.append(field)

    def __iter__(self):
        for field in self.fields:
            self.field = field
            yield
