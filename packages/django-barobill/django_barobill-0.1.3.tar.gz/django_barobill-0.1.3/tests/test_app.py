import unittest
from django_barobill.apps import DjangoBarobillConfig


class TestDjangoBarobill(unittest.TestCase):
    def test_app_name(self):
        self.assertEqual(DjangoBarobillConfig.name, "django_barobill")
