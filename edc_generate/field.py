from django.db.models import CharField

from edc_constants.constants import YES, NO


class Field:

    def __init__(self, context):
        self.attrnames = []
        for attrname, value in context.items():
            if attrname == 'required':
                setattr(self, 'null', value)
            elif attrname in ['editable', 'default']:
                pass
            else:
                setattr(self, attrname, value)
                self.attrnames.append(attrname)
        value = context.pop('required')
        if value == YES:
            context.update({'null': True})
            self.attrnames.append('null')
        if context.get('editable') == NO:
            setattr(self, 'editable', value)
            context.update({'editable': False})
            self.attrnames.append('editable')
        else:
            context.pop('editable')
        if context.get('default'):
            self.attrnames.append('default')
            setattr(self, 'default', value)
        else:
            context.pop('default')
        self.context = context

    def __repr__(self):
        return '{0.name!s}->{0.verbose_name!s}'.format(self)

    def format(self):
        return self.template.format(**self.context)

    @property
    def template(self):
        allowed_attrs = ['verbose_name', 'choices', 'null', 'editable', 'choices', 'default', 'help_text']
        if self.datatype == 'text' or self.datatype == 'text_choice':
            allowed_attrs.insert(2, 'max_length')
            template = self.make_template('models.CharField', allowed_attrs)
        elif self.datatype == 'bigtext':
            allowed_attrs.insert(2, 'max_length')
            template = self.make_template('models.TextField', allowed_attrs)
        elif self.datatype == 'number':
            template = self.make_template('models.IntegerField', allowed_attrs)
        elif self.datatype == 'decimal':
            allowed_attrs.insert(2, 'max_places')
            template = self.make_template('models.DecimalField', allowed_attrs)
        elif self.datatype == 'date':
            template = self.make_template('models.DateField', allowed_attrs)
        elif self.datatype == 'datetime':
            template = self.make_template('models.DateTimeField', allowed_attrs)
        else:
            allowed_attrs.insert(2, 'max_length')
            template = self.make_template('models.CharField', allowed_attrs)
        return template

    def make_template(self, clsname, allowed_attrs):
        attrs = []
        template = self.indent(8) + self.name + ' = ' + clsname + '(\n'
        for attrname in allowed_attrs:
            if attrname == 'verbose_name':
                attrs.append(self.indent(12) + attrname + '=\'{' + attrname + '}\'')
            elif attrname in self.attrnames:
                attrs.append(self.indent(12) + attrname + '={' + attrname + '}')
        template += (',\n'.join(attrs)) + ')\n\n'
        return template

    def indent(self, spaces):
        return ' ' * spaces
