from markupsafe import Markup
from wtforms.widgets.core import html_params


class DivWidget:
    def __init__(self, text='', **kwargs):
        self.text = text

    def __call__(self, field, **kwargs):
        html = []
        kwargs.setdefault("id", field.id)
        html.append("<div %s>" % html_params(**kwargs))
        html.append(self.text)
        html.append("</div>")
        return Markup("".join(html))
