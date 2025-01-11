import io

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from rubymarshal.classes import RubyObject, RubyString, Symbol
from rubymarshal.reader import Reader
from rubymarshal.writer import Writer

TEXT = st.text(alphabet=st.characters(whitelist_categories="L"))
ATTRIBUTES = st.one_of(st.integers(), st.floats(), TEXT)

# RubyObject


@given(TEXT, ATTRIBUTES)
def test_rubyobject_repr(name, attributes):
    obj = RubyObject(name, attributes)
    attr = attributes or {}
    assert obj.__class__.__name__ in str(obj)
    assert repr(attr) in str(obj)
    assert obj.__class__.__name__ in repr(obj)
    assert repr(attr) in repr(obj)


@given(TEXT, ATTRIBUTES, TEXT, ATTRIBUTES)
def test_rubyobject_hash(name1, attributes1, name2, attributes2):
    assume(hash(attributes1) != hash(attributes2) or name1 != name2)
    obj1 = RubyObject(name1, attributes1)
    obj2 = RubyObject(name2, attributes2)
    obj3 = RubyObject(name1, attributes1)
    assert hash(obj1) != hash(obj2)
    assert hash(obj1) == hash(obj3)


# RubyString


@given(TEXT, TEXT)
def test_rubystring_add(t1, t2):
    rstring1 = RubyString(t1)
    rstring2 = RubyString(t2)
    assert (rstring1 + rstring2).text == rstring1.text + rstring2.text


@given(TEXT, TEXT)
def test_rubystring_cmp(t1, t2):
    rstring1 = RubyString(t1)
    rstring2 = RubyString(t2)
    assert (rstring1 < rstring2) == (rstring1.text < rstring2.text)
    assert (rstring1 > rstring2) == (rstring1.text > rstring2.text)
    assert (rstring1 <= rstring2) == (rstring1.text <= rstring2.text)
    assert (rstring1 >= rstring2) == (rstring1.text >= rstring2.text)
    assert (rstring1 != rstring2) == (rstring1.text != rstring2.text)


@given(TEXT, TEXT)
def test_rubystring_repr(t1, t2):
    rstring1 = RubyString(t1)
    rstring2 = RubyString(t2)
    assert repr(rstring1) == repr(t1)
    assert repr(rstring2) == repr(t2)
    assert str(rstring1) == str(t1)
    assert str(rstring2) == str(t2)


@given(TEXT)
def test_rubystring_iter(text):
    rstring = RubyString(text)
    assert len(rstring) == len(text)
    it = iter(rstring)
    for i in text:
        i == next(it)


@given(TEXT)
def test_rubystring_bool(text):
    rstring = RubyString(text)
    assert bool(rstring) == bool(text)


@given(TEXT, st.integers())
def test_rubystring_getitem(text, index):
    assume(len(text) > 0)
    rstring = RubyString(text)
    index %= len(text)
    assert rstring[index] == text[index]


@given(TEXT)
def test_rubystring_hash(text):
    rstring = RubyString(text)
    assert hash(rstring) == hash(text)


# Writer


@given(TEXT)
def test_writer_write_python_object(fd):
    writer = Writer(fd)
    with pytest.raises(ValueError):
        writer.write_python_object(None)


# Reader


def test_reader_read_symbol():
    fd = io.BytesIO(b"\x04\b:\x10test_symbol")

    assert fd.read(1) == b"\x04"
    assert fd.read(1) == b"\x08"

    loader = Reader(fd)
    assert loader.read_symbol() == Symbol("test_symbol")
