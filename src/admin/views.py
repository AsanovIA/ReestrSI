from src.core.mixins import SiteMixin


class IndexView(SiteMixin):
    template = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_list'] = self.get_app_list()

        return context
