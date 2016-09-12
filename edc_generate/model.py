from inspect import getmodule

from edc_base.model.models.base_uuid_model import BaseUuidModel
from edc_consent.model_mixins import RequiresConsentMixin
from edc_metadata.model_mixins import UpdatesCrfMetadataModelMixin
from edc_visit_tracking.model_mixins import CrfModelMixin


class Model:

    def __init__(self, cls_name, bases=None, fields=None, consent_model=None, metas=None, **kwargs):
        self.bases = bases or []
        self.cls_name = cls_name
        self.fields = fields
        self.metas = metas or {'app_label': kwargs.get('app_label')}
        self.consent_model = consent_model
        self.metas['consent_model'] = consent_model
        self.bases.extend(
            [CrfModelMixin, RequiresConsentMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel])

    def to_string(self):
        s = ''
        import_strings = []
        for module_path, objs in self.import_dictionary.items():
            import_strings.append('from {} import {}'.format(module_path, ', '.join(objs)))
        import_strings.sort()
        s += '\n'.join(import_strings) + '\n'
        s += '\n\nclass ' + self.cls_name + '(' + ', '.join([base.__name__ for base in self.bases]) + '):\n\n'
        visit = False
        for field in self.fields or []:
            if not visit:
                s += field.format_visit() or self.indent(8) + '# TODO: {}\n\n'.format(field.visit)
                visit = True
            s += field.format()
        s += self.indent(4) + 'class Meta:\n'
        for attrname, value in self.metas.items():
            s += self.indent(8) + attrname + ' = \'' + value + '\'\n'
        return s

    @property
    def import_dictionary(self):
        import_dictionary = {}
        objects = [obj for obj in self.bases if obj is not None]
        if self.fields:
            for field in self.fields:
                for obj in field.imports:
                    if obj not in objects:
                        objects.append(obj)
        for obj in objects:
            module_path, obj = self.getmodule(obj)
            try:
                import_dictionary[module_path].append(obj)
            except (KeyError, AttributeError):
                import_dictionary[module_path] = [obj]
        return import_dictionary

    def getmodule(self, obj):
        try:
            module_path, obj = obj
        except (TypeError, ValueError):
            module_path = getmodule(obj).__name__
            obj = obj.__name__
        return module_path, obj

    def indent(self, spaces):
        return ' ' * spaces
