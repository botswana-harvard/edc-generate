from django.test import SimpleTestCase

from .field import Field
from edc_constants.choices import YES_NO


class TestGenerate(SimpleTestCase):

    def setUp(self):
        self.context = {
            'name': 'is_martian',
            'datatype': 'text',
            'verbose_name': 'Are you a martian?',
            'max_length': 25,
            'choices': YES_NO,
            'default': None,
            'blank': None,
            'null': None,
            'help_text': 'Please do not answer telepathically',
            'unique': None
        }

    def test_field(self):
        field = Field(self.context)
        field.format()

