from flask import g
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField

from src.db.repository import Repository
from src.utils import FIELDS_EXCLUDE, BLANK_CHOICE, get_model


class SiteForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(g, 'object', None)
        self.fields = []
        for field in self:
            if field.name not in FIELDS_EXCLUDE:
                self.fields.append(field.name)
            label_class = {}
            if getattr(field.flags, 'required', None):
                label_class = {'class': 'required'}
            field.label_class = label_class
            if isinstance(field, SelectField):
                try:
                    model_name = field.render_kw.get('model')
                except AttributeError:
                    raise AttributeError(
                        f'атрибут render_kw поля {field.name} должен быть '
                        f'тип dict и содержать ключ "model"'
                    )
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

                value = self.data[field.name]
                if value is None:
                    value = getattr(instance, f'{field.name}_id', None)
                setattr(field, 'data', value)

    def validate(self, extra_validators=None):
        success = super().validate(extra_validators)
        self.instance = self.update_instance()

        return success

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
