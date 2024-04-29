from itertools import chain
from markupsafe import Markup

from src.core.utils import format_html, try_get_url


class Media:
    def __init__(self, media=None, css=None, js=None):
        if media is not None:
            css = getattr(media, "css", [])
            js = getattr(media, "js", [])
        else:
            if css is None:
                css = []
            if js is None:
                js = []
        self._css_lists = [css]
        self._js_lists = [js]

    def __str__(self):
        return self.render()

    def __html__(self):
        return self

    @property
    def _css(self):
        return self.merge(*self._css_lists)

    @property
    def _js(self):
        return self.merge(*self._js_lists)

    def render(self):
        return Markup(
            "\n".join(
                chain.from_iterable(
                    getattr(self, "render_" + name)() for name in ("css", "js")
                )
            )
        )

    def render_js(self):
        return [
            format_html('<script src="{}"></script>', self.absolute_path(path))
            for path in self._js
        ]

    def render_css(self):
        return [
            format_html(
                '<link href="{}" rel="stylesheet">',
                self.absolute_path(path))
            for path in self._css
        ]

    def absolute_path(self, path):
        if path.startswith(("http://", "https://", "/")):
            return path
        return try_get_url('static', filename=path)

    @staticmethod
    def merge(*lists):
        all_items = set()
        for list_ in filter(None, lists):
            for item in list_:
                all_items.add(item)

        return list(all_items)

    def __add__(self, other):
        combined = Media()
        combined._css_lists = self._css_lists[:]
        combined._js_lists = self._js_lists[:]
        for item in other._css_lists:
            if item and item not in self._css_lists:
                combined._css_lists.append(item)
        for item in other._js_lists:
            if item and item not in self._js_lists:
                combined._js_lists.append(item)
        return combined
