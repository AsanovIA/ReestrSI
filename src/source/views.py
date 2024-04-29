from flask import jsonify, request
from flask.views import View
from sqlalchemy.exc import NoResultFound

from src.db.repository import Repository
from src.core.utils import get_model, EMPTY_VALUE_DISPLAY


class ValueChangeView(View):
    pk = None
    data = None

    def dispatch_request(self, **kwargs):
        self.pk = request.args.get('id')
        self.data = {}
        json_data = {'element': request.args.get('element')}

        if json_data['element'] == 'employee':
            self.get_employee()

        json_data.update(data=self.data)

        return jsonify(json_data)

    def get_employee(self):
        try:
            model = get_model('employee')
            result = Repository.task_get_object(filters=self.pk, model=model)
            self.data.update(division=result.division.name)
        except (AttributeError, NoResultFound):
            self.data.update(division=EMPTY_VALUE_DISPLAY)

