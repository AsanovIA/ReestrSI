from flask import jsonify, request
from flask.views import View
from sqlalchemy.exc import NoResultFound

from src.db.repository import Repository
from src.core.utils import EMPTY_VALUE_DISPLAY, display_for_field, get_model


class ValueChangeView(View):
    pk = None
    data = None

    def dispatch_request(self, **kwargs):
        self.pk = request.args.get('id')
        self.data = {}
        json_data = {'element': request.args.get('element')}

        if json_data['element'] == 'employee':
            self.get_employee()
        if json_data['element'] == 'description_method':
            self.get_description_method()

        json_data.update(data=self.data)

        return jsonify(json_data)

    def get_employee(self):
        self.data.update({
            'division': EMPTY_VALUE_DISPLAY,
            'email': EMPTY_VALUE_DISPLAY
        })
        try:
            model = get_model('employee')
            result = Repository.task_get_object(filters=self.pk, model=model)
            if result.division.name:
                self.data.update(division=result.division.name)
            if result.email:
                self.data.update(email=result.email)
        except (AttributeError, ValueError, NoResultFound):
            pass

    def get_description_method(self):
        self.data.update({
            'description': EMPTY_VALUE_DISPLAY,
            'method': EMPTY_VALUE_DISPLAY
        })
        try:
            model = get_model('description_method')
            result = Repository.task_get_object(filters=self.pk, model=model)
            if result.description:
                value = display_for_field(
                    result.description, model.description, EMPTY_VALUE_DISPLAY
                )
                self.data.update(description=value)
            if result.method:
                value = display_for_field(
                    result.method, model.method, EMPTY_VALUE_DISPLAY
                )
                self.data.update(method=value)
        except (AttributeError, ValueError, NoResultFound):
            pass
