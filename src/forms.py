from flask import g
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField

from src.db.repository import Repository
from src.utils import FIELDS_EXCLUDE, BLANK_CHOICE, get_model


class SiteForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(g, 'object', None)
        if instance is None:
            return
        self.fields = []
        for field in self:
            if field.name not in FIELDS_EXCLUDE:
                self.fields.append(field.name)
            if field.render_kw is None:
                field.render_kw = {}
            label_class = {}
            if getattr(field.flags, 'required', None):
                label_class = {'class': 'required'}
            field.label_class = label_class
            if isinstance(field, SelectField):
                model_name = field.render_kw.get('model')
                if model_name is None:
                    raise KeyError(
                        f'Отсутствует ключ "model" параметра "render_kw" для '
                        f'{field.name} класса {self.__class__.__name__}'
                    )
                model_related = get_model(model_name)
                kwargs = {'model': model_related}
                choices = [
                    (obj.id, obj)
                    for obj in Repository.task_get_list(**kwargs)
                ]
                choices = BLANK_CHOICE + choices
                setattr(field, 'choices', choices)

            field.is_readonly = field.render_kw.get('readonly', False)
            if not field.is_readonly:
                value = self.data[field.name]
                if value is None:
                    value = getattr(instance, f'{field.name}_id', None)
                setattr(field, 'data', value)

    def contents(self, field):
        from sqlalchemy.orm import Relationship
        from src.utils import (
            boolean_icon, lookup_field, display_for_field, EMPTY_VALUE_DISPLAY
        )

        obj = g.object
        try:
            f, attr, value = lookup_field(field.name, obj)
        except (AttributeError, ValueError):
            result_repr = EMPTY_VALUE_DISPLAY
            if field.data is not None:
                result_repr = field.data
        else:
            if f is None:
                if getattr(attr, "boolean", False):
                    result_repr = boolean_icon(value)
                else:
                    result_repr = value
            else:
                if (
                    isinstance(f.property, Relationship)
                    and value is not None
                ):
                    result_repr = str(value)
                else:
                    result_repr = display_for_field(value, f.type, EMPTY_VALUE_DISPLAY)

        return result_repr

    def validate(self, extra_validators=None):
        validate = super().validate(extra_validators)
        if not validate:
            return validate
        self.instance = self.update_instance()
        post_validate = self.post_validate()

        return validate and post_validate

    def post_validate(self):
        return True

    def update_instance(self):
        model = g.model
        exclude = getattr(getattr(self, 'Meta', None), 'exclude', None)
        instance = g.object

        for field in self:
            if not hasattr(model, field.name) or field.name not in self.data:
                continue
            if exclude is not None and field.name in exclude:
                continue
            if isinstance(field, SelectField):
                setattr(instance, f'{field.name}_id', self.data[field.name])
            else:
                value = self.data[field.name]
                value = value if value != '' else None
                setattr(instance, field.name, value)

        return instance
