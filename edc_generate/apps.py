import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings

from edc_base.apps import AppConfig as EdcBaseAppConfigParent


class AppConfig(DjangoAppConfig):
    name = 'edc_generate'

    def ready(self):
        sys.stdout.write('* media root: {}\n'.format(settings.MEDIA_ROOT))


class EdcBaseAppConfig(EdcBaseAppConfigParent):
    institution = 'Botswana-HarvardAIDS Institute'
    project_name = 'Edc Generate'
