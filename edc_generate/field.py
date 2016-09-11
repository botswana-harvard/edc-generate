import copy

from django.db import models
from edc_constants.constants import YES, NO
from edc_constants import choices as edc_choices
from edc_constants.choices import *


class Field:

    non_field_attrs = ['name', 'datatype', 'visit', 'model']
    field_attrs = ['verbose_name', 'null', 'blank', 'validators',
                   'editable', 'default', 'help_text', 'unique']

    def __init__(self, context):
        self.name = context.get('name')
        self.verbose_name = context.get('verbose_name')
        self.imports = [('django.db', 'models')]
        self.attrnames = []
        self.allowed_attrs = copy.deepcopy(self.field_attrs)
        self.context = copy.deepcopy(context)
        for attrname, value in context.items():
            if attrname in self.non_field_attrs:
                setattr(self, attrname, value)
                self.attrnames.append(attrname)
            if attrname == 'choices' and self.context.get('choices'):
                self.update_choices()
            if attrname == 'validators' and self.context.get('validators'):
                self.update_validators()
            for key in ['default', 'choices', 'help_text', 'validators']:
                self.set_or_pop_from_context(key)
            for key in ['editable']:
                self.set_or_pop_from_context(
                    key, lambda x: True if x == YES else False, keep_if_false=True)
            for key in ['null', 'blank', 'unique']:
                self.set_or_pop_from_context(
                    key, lambda x: True if x == YES else False, keep_if_true=True)
        self.imports = list(set(self.imports))

    def __repr__(self):
        return '{0.name!s}'.format(self)

    def set_or_pop_from_context(self, key, value_map=None, keep_if_true=None, keep_if_false=None):
        """Conditionally remove a context key and/or map a context value.

        value map may be a lambda or dictionary, e.g. {'Yes': True, 'No': False}"""
        value = self.context.get(key)
        if value:
            if value_map:
                try:
                    value = value_map(value)
                except TypeError:
                    value = value_map.get(value)
            keep = True
            if (value is False and keep_if_true) or (value is True and keep_if_false):
                keep = False
            if keep:
                self.attrnames.append(key)
                self.context[key] = value
                setattr(self, key, value)

        else:
            if key in self.context:
                self.context.pop(key)

    def format(self):
        return self.template.format(**self.context)

    def format_visit(self):
        pass

    @property
    def template(self):
        attrs = []
        template = self.indent(8) + self.name + ' = ' + self.cls_name + '(\n'
        allowed_attrs = [attr for attr in self.allowed_attrs if attr in self.context]
        for attrname in allowed_attrs:
            if attrname == 'verbose_name':
                attrs.append(self.indent(12) + attrname + '=\'{' + attrname + '}\'')
            elif attrname == 'default':
                if 'CharField' in self.cls_name:
                    attrs.append(self.indent(12) + attrname + '=\'{' + attrname + '}\'')
                else:
                    attrs.append(self.indent(12) + attrname + '={' + attrname + '}')
            elif attrname in self.attrnames:
                attrs.append(self.indent(12) + attrname + '={' + attrname + '}')
        template += (',\n'.join(attrs)) + ')\n\n'
        return template

    @property
    def cls_name(self):
        if self.datatype == 'text':
            cls_name = 'models.CharField'
            self.allowed_attrs.insert(2, 'max_length')
        elif self.datatype == 'text_choice':
            cls_name = 'models.CharField'
            self.allowed_attrs.insert(2, 'max_length')
            self.allowed_attrs.insert(3, 'choices')
        elif self.datatype == 'bigtext':
            cls_name = 'models.TextField'
            self.allowed_attrs.insert(2, 'max_length')
        elif self.datatype == 'number':
            cls_name = 'models.IntegerField'
        elif self.datatype == 'decimal':
            cls_name = 'models.DecimalField'
            self.allowed_attrs.insert(2, 'max_places')
        elif self.datatype == 'date':
            cls_name = 'models.DateField'
        elif self.datatype == 'datetime':
            cls_name = 'models.DateTimeField'
        else:
            cls_name = 'models.CharField'
            self.allowed_attrs.insert(2, 'max_length')
        return cls_name

    def update_choices(self):
        choices = self.context.get('choices')
        c = []
        try:
            for choice in choices.split(';'):
                try:
                    store, display = choice.split(':')
                except ValueError:
                    store = '_'.join(choice.split(' ')).lower()
                    display = choice
                c.append((store, display))
            self.context['choices'] = tuple(c)
        except AttributeError:
            self.context['choices'] = choices
        for choice in [c for c in dir(edc_choices) if not c.startswith('_')]:
            if self.context['choices'] == eval(choice):
                self.context['choices'] = choice
                self.imports.append(('edc_constants.choices', choice))

    def update_validators(self):
        self.context['validators'] = '[],  # TODO: {}'.format(self.context['validators'])

    def indent(self, spaces):
        return ' ' * spaces
