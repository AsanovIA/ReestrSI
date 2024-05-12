from flask import g, request
from sqlalchemy import Boolean, Date
from sqlalchemy.orm import Relationship

from src.core.constants import FILTER_SUFFIX, LOOKUP_SEP
from src.core.fields import FilterSelectField, FilterDateField
from src.core.utils import label_for_field


class FilterForm:
    def __init__(self):
        self.filters = []
        relation_filters, boolean_filters, date_filters = [], [], []
        for name in g.fields_filter:
            model = g.model
            field_name = name
            if LOOKUP_SEP in name:
                lookup_fields = name.split(LOOKUP_SEP)
                for index, path_part in enumerate(lookup_fields):
                    field = getattr(model, path_part)
                    field_name = path_part
                    if (
                            isinstance(field.property, Relationship)
                            and index < len(lookup_fields) - 1
                    ):
                        model = field.property.entity.class_

            field = getattr(model, field_name)
            title = label_for_field(field_name, model=field.class_)

            filter_name = '%s__%s' % (name, FILTER_SUFFIX)
            id = '%s__id' % name
            data = request.args.get(filter_name)
            kwargs = {
                'field_name': name,
                'field': field,
                'title': title,
                'options': {
                    'name': filter_name,
                    'id': id,
                    'data': data,
                }
            }

            if isinstance(field.property, Relationship):
                filter_ = RelatedListFilter(**kwargs)
                relation_filters.append(filter_)
            elif isinstance(field.type, Boolean):
                filter_ = BooleanListFilter(**kwargs)
                boolean_filters.append(filter_)
            elif isinstance(field.type, Date):
                filter_ = DateListFilter(**kwargs)
                date_filters.append(filter_)
            else:
                raise Exception(f'Фильтра для {field.key} нет')

        self.filters = relation_filters + boolean_filters + date_filters

    def __iter__(self):
        return iter(self.filters)


class ListFilter:
    field = None

    def __init__(self, title, options, **kwargs):
        self.title = title
        self.options = options

    def __str__(self):
        return self.field()

    def __html__(self):
        return self.field()


class RelatedListFilter(ListFilter):
    def __init__(self, field, **kwargs):
        super().__init__(**kwargs)
        self.type = 'select'
        self.options.update(model=field.property.argument)
        self.field = FilterSelectField(**self.options)


class BooleanListFilter(ListFilter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'boolean'
        choices = [('1', 'Да'), ('0', 'Нет')]
        self.options.update(choices=choices)
        self.field = FilterSelectField(**self.options)


class DateListFilter(ListFilter):
    def __init__(self, field_name, **kwargs):
        super().__init__(**kwargs)
        self.type = 'date'
        self.fields = []
        for suffix in ['__begin', '__end']:
            field_name_suffix = field_name + suffix
            filter_name = '%s__%s' % (field_name_suffix, FILTER_SUFFIX)
            id = '%s__id' % field_name_suffix
            data = request.args.get(filter_name, '')
            self.options.update({
                'name': filter_name,
                'id': id,
                'data': data
            })
            field = FilterDateField(**self.options)
            self.fields.append(field)

    def __iter__(self):
        for field in self.fields:
            self.field = field
            yield
