import os

from flask import g, request
from flask_wtf import FlaskForm
from werkzeug.datastructures import FileStorage

from . import ExtendedFileField, ExtendedSelectField
from .utils import (
    FIELDS_EXCLUDE,
    label_for_field,
    secure_filename,
    try_get_url,
    upload_for_field,
)


class SiteForm(FlaskForm):
    def __init__(
            self,
            obj=None,
            fields=None,
            exclude=None,
            readonly_fields=None,
            *args,
            **kwargs
    ):
        super().__init__(obj=obj, *args, **kwargs)
        self.instance = obj or g.model()
        self.readonly_fields = (
                readonly_fields or list(self.get_readonly_fields())
        )
        exclude = exclude or getattr(getattr(self, 'Meta', []), 'exclude', [])
        self.exclude = list(exclude) + FIELDS_EXCLUDE
        self.changed_data = []
        self.fields = []
        fields = fields or getattr(self.Meta, 'fields', None)
        self.set_attributes(fields)

    def set_attributes(self, fields):
        def set_field_attributes():
            #  Установка label полей формы
            field.label.text = label_for_field(field.name, form=self) + ':'

            field.label_class = {}
            if (
                    getattr(field.flags, 'required', None)
                    and field.name not in self.readonly_fields
            ):
                field.label_class = {'class': 'required'}

            field.is_readonly = False
            if field.name in self.readonly_fields:
                field.is_readonly = True
                field.description = ''

            if isinstance(field, ExtendedFileField):
                self.is_multipart = True
                field.upload = upload_for_field(field.name)
                if (
                        request.method == 'POST'
                        and isinstance(field.data, FileStorage)
                ):
                    filename = getattr(field.data, 'filename')
                    if filename:
                        filename = secure_filename(filename)
                else:
                    filename = field.data
                if not filename:
                    return
                field.filename = filename
                path_file = os.path.join(field.upload, filename)
                field.url = try_get_url('source.view_file', filename=path_file)

            #  Установка выбранных значений в Select формы
            if isinstance(
                    field, ExtendedSelectField) and not field.is_readonly:
                value = getattr(self.instance, f'{field.name}_id', None)
                if request.method == 'POST':
                    value = self.data[field.name]
                field.data = str(value) if value is not None else ''

        if fields:
            for field_name in fields:
                field = self[field_name]
                self.fields.append(field)
                set_field_attributes()
        else:
            for field in self:
                if field.name in self.exclude:
                    continue
                self.fields.append(field)
                set_field_attributes()

    def get_readonly_fields(self, readonly_fields=None):
        if readonly_fields is None:
            readonly_fields = []
        return getattr(
            getattr(self, 'Meta', []), 'readonly_fields', []
        ) + readonly_fields

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
        instance = self.instance

        for field in self.fields:
            if not hasattr(model, field.name) or field.name not in self.data:
                continue
            if self.exclude is not None and field.name in self.exclude:
                continue
            if self.readonly_fields and field.name in self.readonly_fields:
                continue
            if isinstance(field, ExtendedFileField):
                continue

            value = self.data[field.name]
            if isinstance(field, ExtendedSelectField):
                value = int(value) if value else None
                setattr(instance, f'{field.name}_id', value)

            else:
                value = value if value != '' else None
                setattr(instance, field.name, value)

        return instance

    def check_changed_data(self):
        model = g.model
        instance = self.instance

        changed_fields = []
        for field in self.fields:
            if not hasattr(model, field.name) or field.name not in self.data:
                continue
            if self.exclude is not None and field.name in self.exclude:
                continue
            if self.readonly_fields and field.name in self.readonly_fields:
                continue

            if isinstance(field, ExtendedFileField) and field.filename:
                old_filename = getattr(instance, field.name, None)
                if (
                        field.filename != old_filename
                        or f'{field.name}_clear' in request.form
                ):
                    changed_fields.append(field)
                continue

            value = self.data[field.name]
            if isinstance(field, ExtendedSelectField):
                value = int(value) if value else None
                old_value = getattr(instance, f'{field.name}_id')
            else:
                value = value if value != '' else None
                old_value = getattr(instance, field.name)

            if value != old_value:
                changed_fields.append(field)

        return changed_fields
