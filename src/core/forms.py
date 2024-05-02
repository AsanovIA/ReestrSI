import os

from flask import g, request
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename

from . import ExtendedFileField, ExtendedSelectField
from .utils import FIELDS_EXCLUDE, try_get_url, label_for_field


class SiteForm(FlaskForm):
    def __init__(self, obj, *args, **kwargs):
        super().__init__(obj=obj, *args, **kwargs)
        readonly_fields = getattr(
            getattr(self, 'Meta', []), 'readonly_fields', []
        )
        self.instance = obj
        self.changed_data = []
        self.fields = []
        for field in self:
            if field.name not in FIELDS_EXCLUDE:
                self.fields.append(field.name)
                #  Установка label полей формы
                field.label.text = label_for_field(field.name, self) + ':'
            if getattr(field.flags, 'required', None):
                field.label_class = {'class': 'required'}
            else:
                field.label_class = {}
            field.is_readonly = (
                True if field.name in readonly_fields else False
            )

            if isinstance(field, ExtendedFileField):
                self.is_multipart = True
                if field.object_data is None:
                    continue
                path_file = os.path.join(field.upload, field.object_data)
                field.url = try_get_url('source.view_file', filename=path_file)

            #  Установка выбранных значений в Select формы
            if isinstance(
                    field, ExtendedSelectField) and not field.is_readonly:
                value = self.data[field.name]
                if value is None:
                    value = getattr(obj, f'{field.name}_id', None)
                field.data = value

    def contents(self, field):
        from sqlalchemy.orm import Relationship
        from src.core.utils import (
            boolean_icon, lookup_field, display_for_field, EMPTY_VALUE_DISPLAY
        )

        try:
            f, attr, value = lookup_field(field.name, self.instance)
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
                    result_repr = display_for_field(
                        value, f.type, EMPTY_VALUE_DISPLAY
                    )

        return result_repr

    def validate(self, extra_validators=None):
        validate = super().validate(extra_validators)
        if not validate:
            return validate
        self.instance, self.changed_data = self.update_instance()
        post_validate = self.post_validate()

        return validate and post_validate

    def has_changed(self):
        return bool(self.changed_data)

    def post_validate(self):
        return True

    def update_instance(self):
        model = g.model
        exclude = getattr(getattr(self, 'Meta', None), 'exclude', None)
        instance = self.instance

        changed_fields = []
        for field in self:
            if not hasattr(model, field.name) or field.name not in self.data:
                continue
            if exclude is not None and field.name in exclude:
                continue

            if isinstance(field, ExtendedFileField):
                filename = secure_filename(request.files[field.name].filename)
                if (
                        filename
                        and getattr(instance, field.name)
                        and filename != getattr(instance, field.name)
                        or f'{field.name}_clear' in request.form
                ):
                    changed_fields.append(field)
                continue

            elif isinstance(field, ExtendedSelectField):
                value = self.data[field.name]
                value = value if value != 0 else None
                if value != getattr(instance, f'{field.name}_id'):
                    changed_fields.append(field)
                setattr(instance, f'{field.name}_id', value)

            else:
                value = self.data[field.name]
                value = value if value != '' else None
                if value != getattr(instance, field.name):
                    changed_fields.append(field)
                setattr(instance, field.name, value)

        return instance, changed_fields
