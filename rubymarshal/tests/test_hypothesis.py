from unittest import TestCase

# noinspection PyPackageRequirements
from hypothesis import given

# noinspection PyPackageRequirements
from hypothesis.strategies import integers, lists, booleans, floats, dictionaries, text
import math
from rubymarshal.reader import loads
from rubymarshal.writer import writes

__author__ = "Matthieu Gallet"


class TestValues(TestCase):
    def read_write(self, x):
        self.assertEqual(loads(writes(x)), x)

    @given(integers())
    def test_ints(self, x):
        self.read_write(x)

    @given(lists(integers()))
    def test_lists(self, x):
        self.read_write(x)

    @given(lists(booleans()))
    def test_booleans(self, x):
        self.read_write(x)

    @given(floats())
    def test_floats(self, x):
        if math.isnan(x):
            self.assertTrue(math.isnan(loads(writes(x))))
        else:
            self.read_write(x)

    @given(dictionaries(integers(), integers()))
    def test_dictionaries(self, x):
        self.read_write(x)

    @given(lists(text()))
    def test_text(self, x):
        self.read_write(x)
