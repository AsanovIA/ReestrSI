from markupsafe import Markup
from wtforms.widgets.core import html_params, FileInput


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


class ExtendedFileInput(FileInput):
    def __call__(self, field, **kwargs):
        input_ = super().__call__(field, **kwargs)
        if field.data:
            html = ('<div><div class="flex-container">'
                    '<label>сейчас используется: </label>'
                    '<a href="{}" target="_blank">{}</a></div>').format(
                field.url, field.filename
            )

            if not getattr(field.flags, 'required', False):
                checkbox_name = field.name + '_clear'
                checkbox_id = checkbox_name + '_id'

                html += ('<div class="flex-container">'
                         '<input type="checkbox" name="%(name)s" id="%(id)s">'
                         '<label for="%(id)s">очистить</label></div>'
                         ) % {'name': checkbox_name, 'id': checkbox_id}

            html += '<div class="flex-container"><label>изменить: </label>'
            input_ = Markup(html) + input_ + Markup('</div></div>')

        return input_
