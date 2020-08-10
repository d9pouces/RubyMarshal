import io
from unittest import TestCase

# noinspection PyPackageRequirements
from hypothesis import strategies as st, given, assume

from rubymarshal.classes import RubyObject, RubyString, Symbol
from rubymarshal.reader import Reader
from rubymarshal.writer import Writer

TEXT = st.text(alphabet=st.characters(whitelist_categories="L"))
ATTRIBUTES = st.one_of(st.integers(), st.floats(), TEXT)


# RubyObject
class TestRubyObject(TestCase):
    @given(TEXT, ATTRIBUTES)
    def test_rubyobject_repr(self, name, attributes):
        obj = RubyObject(name, attributes)
        attr = attributes or {}
        self.assertIn(obj.__class__.__name__, str(obj))
        self.assertIn(repr(attr), str(obj))
        self.assertIn(obj.__class__.__name__, repr(obj))
        self.assertIn(repr(attr), repr(obj))

    @given(TEXT, ATTRIBUTES, TEXT, ATTRIBUTES)
    def test_rubyobject_hash(self, name1, attributes1, name2, attributes2):
        assume(hash(attributes1) != hash(attributes2))
        obj1 = RubyObject(name1, attributes1)
        obj2 = RubyObject(name2, attributes2)
        obj3 = RubyObject(name1, attributes1)
        self.assertNotEqual(hash(obj1), hash(obj2))
        self.assertEqual(hash(obj1), hash(obj3))


# RubyString
class TestRubyString(TestCase):
    @given(TEXT, TEXT)
    def test_rubystring_add(self, t1, t2):
        rstring1 = RubyString(t1)
        rstring2 = RubyString(t2)
        self.assertEqual((rstring1 + rstring2).text, rstring1.text + rstring2.text)

    @given(TEXT, TEXT)
    def test_rubystring_cmp(self, t1, t2):
        rstring1 = RubyString(t1)
        rstring2 = RubyString(t2)
        self.assertEqual((rstring1 < rstring2), (rstring1.text < rstring2.text))
        self.assertEqual((rstring1 > rstring2), (rstring1.text > rstring2.text))
        self.assertEqual((rstring1 <= rstring2), (rstring1.text <= rstring2.text))
        self.assertEqual((rstring1 >= rstring2), (rstring1.text >= rstring2.text))
        self.assertEqual((rstring1 != rstring2), (rstring1.text != rstring2.text))

    @given(TEXT, TEXT)
    def test_rubystring_repr(self, t1, t2):
        rstring1 = RubyString(t1)
        rstring2 = RubyString(t2)
        self.assertEqual(repr(rstring1), repr(t1))
        self.assertEqual(repr(rstring2), repr(t2))
        self.assertEqual(str(rstring1), str(t1))
        self.assertEqual(str(rstring2), str(t2))

    @given(TEXT)
    def test_rubystring_iter(self, text):
        rstring = RubyString(text)
        self.assertEqual(len(rstring), len(text))
        it = iter(rstring)
        for i in text:
            self.assertEqual(i, next(it))

    @given(TEXT)
    def test_rubystring_bool(self, text):
        rstring = RubyString(text)
        self.assertEqual(bool(rstring), bool(text))

    @given(TEXT, st.integers())
    def test_rubystring_getitem(self, text, index):
        assume(len(text) > 0)
        rstring = RubyString(text)
        index %= len(text)
        self.assertEqual(rstring[index], text[index])

    @given(TEXT)
    def test_rubystring_hash(self, text):
        rstring = RubyString(text)
        self.assertEqual(hash(rstring), hash(text))


# Writer
class TestBasicWriter(TestCase):
    @given(TEXT)
    def test_writer_write_python_object(self, fd):
        writer = Writer(fd)
        with self.assertRaises(ValueError):
            writer.write_python_object(None)


# Reader
class TestReadSymbol(TestCase):
    def test_reader_read_symbol(self):
        fd = io.BytesIO(b"\x04\b:\x10test_symbol")

        assert fd.read(1) == b"\x04"
        assert fd.read(1) == b"\x08"

        loader = Reader(fd)
        self.assertEqual(loader.read_symbol(), Symbol("test_symbol"))
