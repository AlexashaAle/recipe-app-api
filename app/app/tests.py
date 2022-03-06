from django.test import TestCase

from app.calc import add


class CalcTests(TestCase):
    """Test for calc function"""

    def test_add_numbers(self):
        """Test that values are added together"""
        self.assertEqual(add(3, 8), 11)




