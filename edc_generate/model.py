
class Model:

    def __init__(self, cls_name, bases, fields, metas=None, **kwargs):
        self.cls_name = cls_name
        self.bases = bases
        self.fields = fields
        self.metas = metas or {'app_label': kwargs.get('app_label')}

    def to_string(self):
        s = 'class ' + self.cls_name + '(' + ', '.join(self.bases) + '):\n\n'
        for field in self.fields:
            s += field
        s += self.indent(4) + 'class Meta:\n'
        for attrname, value in self.metas.items():
            s += self.indent(8) + attrname + ' = \'' + value + '\''
        return s

    def indent(self, spaces):
        return ' ' * spaces
