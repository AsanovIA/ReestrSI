import os

from flask import g, request
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename

from . import ExtendedFileField, ExtendedSelectField
from .utils import (
    FIELDS_EXCLUDE, label_for_field, try_get_url, upload_for_field
)


class SiteForm(FlaskForm):
    def __init__(self, obj, *args, **kwargs):
        super().__init__(obj=obj, *args, **kwargs)
        try:
            fields = getattr(self.Meta, 'fields')
        except AttributeError:
            fields = None

        readonly_fields = getattr(
            getattr(self, 'Meta', []), 'readonly_fields', []
        )
        self.instance = g.model() if obj is None else obj
        self.changed_data = []
        self.fields = []

        def set_attributes():
            #  Установка label полей формы
            field.label.text = label_for_field(field.name, form=self) + ':'
            if getattr(field.flags, 'required', None):
                field.label_class = {'class': 'required'}
            else:
                field.label_class = {}
            field.is_readonly = (
                True if field.name in readonly_fields else False
            )

            if isinstance(field, ExtendedFileField):
                self.is_multipart = True
                field.upload = upload_for_field(field.name)
                if request.method == 'POST':
                    value = getattr(field.data, 'filename', None)
                else:
                    value = field.data
                if not value:
                    return
                field.filename = value
                path_file = os.path.join(field.upload, field.filename)
                field.url = try_get_url('source.view_file', filename=path_file)

            #  Установка выбранных значений в Select формы
            if isinstance(
                    field, ExtendedSelectField) and not field.is_readonly:
                value = getattr(self.instance, f'{field.name}_id', None)
                if request.method == 'POST':
                    value = self.data[field.name]
                field.data = str(value)

        if fields:
            for field_name in fields:
                field = self[field_name]
                self.fields.append(field)
                set_attributes()
        else:
            for field in self:
                if field.name in FIELDS_EXCLUDE:
                    continue
                self.fields.append(field)
                set_attributes()

    def contents(self, field):
        from sqlalchemy.orm import Relationship
        from src.core import (
            boolean_icon, lookup_field, display_for_field, EMPTY_VALUE_DISPLAY
        )

        try:
            f, attr, value = lookup_field(field.name, self.instance)
        except (AttributeError, ValueError):
            result_repr = EMPTY_VALUE_DISPLAY
        else:
            if f is None:
                if getattr(attr, "boolean", False):
                    result_repr = boolean_icon(value)
                else:
                    if hasattr(value, "__html__"):
                        result_repr = value
                    else:
                        result_repr = str(value)
            else:
                if (
                        isinstance(f.property, Relationship)
                        and value is not None
                ):
                    result_repr = str(value)
                else:
                    result_repr = display_for_field(
                        value, f, EMPTY_VALUE_DISPLAY
                    )

        return result_repr

    def validate(self, extra_validators=None):
        validate = super().validate(extra_validators)
        self.changed_data = self.check_changed_data()
        self.instance = self.update_instance()
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

        for field in self:
            if not hasattr(model, field.name) or field.name not in self.data:
                continue
            if exclude is not None and field.name in exclude:
                continue

            value = self.data[field.name]
            if isinstance(field, ExtendedSelectField):
                value = int(value) if value != '' else None
                setattr(instance, f'{field.name}_id', value)

            else:
                value = value if value != '' else None
                setattr(instance, field.name, value)

        return instance

    def check_changed_data(self):
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
                        and hasattr(instance, field.name)
                        and filename != getattr(instance, field.name)
                        or f'{field.name}_clear' in request.form
                ):
                    changed_fields.append(field)
                continue

            value = self.data[field.name]
            if isinstance(field, ExtendedSelectField):
                value = int(value) if value != '' else None
                if value != getattr(instance, f'{field.name}_id'):
                    changed_fields.append(field)

            else:
                value = value if value != '' else None
                if value != getattr(instance, field.name):
                    changed_fields.append(field)

        return changed_fields
