from django.test import TestCase

from investment.functions import mvo


class OptimizeTestCase(TestCase):
    def test_close_price(self):
        o = mvo.Optimize()
        o.prepare()
        self.assertEqual(1, 1)
