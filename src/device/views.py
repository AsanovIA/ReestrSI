from src.mixins import ListMixin


class ListObjectView(ListMixin):
    model_name = 'si'
    fields_link = None
    decorators = []