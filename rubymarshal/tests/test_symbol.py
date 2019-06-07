from unittest import TestCase
from rubymarshal.classes import Symbol

__author__ = "Matthieu Gallet"


class TestSymbol(TestCase):
    def test_symbols(self):
        a = Symbol("test1")
        b = Symbol("test2")
        c = Symbol("test1")
        self.assertNotEqual(a, b)
        self.assertEqual(a, c)
        self.assertEqual(id(a), id(c))
