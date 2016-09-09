import csv
import os

from django.conf import settings
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin

from .field import Field
from .model import Model


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_generate/home.html'
    csv_filename = os.path.join(settings.MEDIA_ROOT, 'test_dd.csv')
    model_class_template = 'edc_generate/models/crf.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            'cls_name': 'CrfModel',
            'bases': ['EdcBaseModelMixin'],
            'app_label': 'test_app',
        })
        context.update({
            'code': self.get_rendered_code(context)
        })
        return context

    @property
    def data_dictionary(self):
        data_dictionary = []
        header_row = None
        with open(self.csv_filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if not header_row:
                    header_row = row
                else:
                    data_dictionary.append(Field(row))
        return data_dictionary

    def get_rendered_code(self, context):
        field_attrs = [field.format() for field in self.data_dictionary]
        code = Model(context.get('cls_name'), context.get('bases'),
                     field_attrs, {'app_label': 'test_app'}).to_string()
        return highlight(code, PythonLexer(), HtmlFormatter())
