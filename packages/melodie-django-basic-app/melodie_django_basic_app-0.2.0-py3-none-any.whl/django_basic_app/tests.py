from django.test import TestCase
from .models import Exemple

class ExempleTestCase(TestCase):
    def setUp(self):
        Exemple.objects.create(nom="Test")

    def test_str(self):
        exemple = Exemple.objects.get(nom="Test")
        self.assertEqual(str(exemple), "Test")
