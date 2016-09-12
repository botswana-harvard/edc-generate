import csv
import os

from django.conf import settings
from django.views.generic.base import TemplateView

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin

from .field import Field
from .model import Model


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_generate/home.html'
    csv_fields = os.path.join(settings.MEDIA_ROOT, 'bm_fields.csv')
    csv_models = os.path.join(settings.MEDIA_ROOT, 'bm_models.csv')
    model_class_template = 'edc_generate/models/crf.html'

    def __init__(self, **kwargs):
        self._fields = {}
        super(HomeView, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            'code': self.render_models(context)
        })
        return context

    @property
    def models(self):
        models = {}
        header_row = None
        with open(self.csv_models, newline='') as f:
            reader = csv.DictReader(f, delimiter=',', quotechar='"')
            for row in reader:
                if not header_row:
                    header_row = row
                else:
                    model = Model(row['model_name'], fields=self.fields.get(row['model_name']), **row)
                    models.update({row['model_name']: model})
        return models

    @property
    def fields(self):
        if not self._fields:
            header_row = None
            with open(self.csv_fields, newline='') as f:
                reader = csv.DictReader(f, delimiter=',', quotechar='"')
                for row in reader:
                    if not header_row:
                        header_row = row
                    else:
                        try:
                            self._fields[row['model']].append(Field(row))
                        except KeyError:
                            self._fields[row['model']] = [Field(row)]
        return self._fields

    def render_models(self, context):
        rendered = ''
        for model in self.models.values():
            rendered += highlight(model.to_string(), PythonLexer(), HtmlFormatter())
        return rendered
