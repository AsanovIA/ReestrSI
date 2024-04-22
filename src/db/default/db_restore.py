from src.db.default.db_data import default_data
from src.db.repository import Repository

from src.utils import get_model


def set_default_db():
    Repository.recreate_table()
    table_name = ['NameSi', 'TypeSi']
    for model_name, value in default_data.items():
        model = get_model(model_name)
        if isinstance(value, str) and model_name in table_name:
            values = [{'name': f'{value} {i + 1}'} for i in range(3)]
        else:
            values = value

        Repository.bulk_insert(model, values)
