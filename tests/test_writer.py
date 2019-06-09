import io
import math
import re
from unittest import TestCase

from rubymarshal.classes import UsrMarshal, Symbol
from rubymarshal.reader import loads
from rubymarshal.writer import Writer, writes

__author__ = "Matthieu Gallet"


def long_write(obj):
    fd = io.BytesIO()
    writer = Writer(fd)
    writer.write_long(obj)
    return fd.getvalue()


class Constant:
    def __init__(self, name):
        self.name = name


class ConstantWriter(Writer):
    def write_python_object(self, obj):
        if isinstance(obj, Constant):
            return self.write(Symbol(obj.name))
        super().write_python_object(obj)


class CustomWriter(TestCase):
    def test_write_constant(self):
        dumped = writes([Constant("test")], cls=ConstantWriter)
        read_constant = loads(dumped)
        self.assertEqual([Symbol("test")], read_constant)


class TestWriteLong(TestCase):
    def test_0(self):
        self.assertEqual(b"\x00", long_write(0))

    def test_1(self):
        self.assertEqual(b"\x06", long_write(1))

    def test_122(self):
        self.assertEqual(b"\x7F", long_write(122))

    def test_123(self):
        self.assertEqual(b"\x01{", long_write(123))

    def test_255(self):
        self.assertEqual(b"\x01\xFF", long_write(255))

    def test_256(self):
        self.assertEqual(b"\x02\x00\x01", long_write(256))

    def test_65535(self):
        self.assertEqual(b"\x02\xFF\xFF", long_write(65535))

    def test_65536(self):
        self.assertEqual(b"\x03\x00\x00\x01", long_write(65536))

    def test_65537000(self):
        self.assertEqual(b"\x04\xE8\x03\xE8\x03", long_write(65537000))

    def test__1(self):
        self.assertEqual(b"\xFA", long_write(-1))

    def test__123(self):
        self.assertEqual(b"\x80", long_write(-123))

    def test__124(self):
        self.assertEqual(b"\xFF\x84", long_write(-124))

    def test__256(self):
        self.assertEqual(b"\xfe\x00\xff", long_write(-256))

    def test__512(self):
        self.assertEqual(b"\xfe\x00\xfe", long_write(-512))

    def test__768(self):
        self.assertEqual(b"\xFE\x00\xFD", long_write(-768))

    def test__257(self):
        self.assertEqual(b"\xFE\xFF\xFE", long_write(-257))

    def test__259(self):
        self.assertEqual(b"\xFE\xFD\xFE", long_write(-259))

    def test__65536(self):
        self.assertEqual(b"\xfd\x00\x00\xff", long_write(-65536))

    def test__65537(self):
        self.assertEqual(b"\xFD\xFF\xFF\xFE", long_write(-65537))

    def test__65537000(self):
        self.assertEqual(b"\xFC\x18\xFC\x17\xFC", long_write(-65537000))


class TestIdemPotent(TestCase):
    def read_write(self, x):
        self.assertEqual(loads(writes(x)), x)


class TestLong(TestIdemPotent):
    def test_0(self):
        self.read_write(0)

    def test_1(self):
        self.read_write(1)

    def test_122(self):
        self.read_write(122)

    def test_123(self):
        self.read_write(123)

    def test_255(self):
        self.read_write(255)

    def test_256(self):
        self.read_write(256)

    def test_65536(self):
        self.read_write(65536)

    def test_65535(self):
        self.read_write(65535)

    def test_65537000(self):
        self.read_write(65537000)

    def test__1(self):
        self.read_write(-1)

    def test__123(self):
        self.read_write(-123)

    def test__124(self):
        self.read_write(-124)

    def test__256(self):
        self.read_write(-256)

    def test__257(self):
        self.read_write(-257)

    def test__259(self):
        self.read_write(-259)

    def test__65536(self):
        self.read_write(-65536)

    def test__65537(self):
        self.read_write(-65537)

    def test__65537000(self):
        self.read_write(-65537000)

    def test_long(self):
        self.read_write(1234567890123456789)

    def test_longlong(self):
        self.read_write(
            1234567890123456789012343294802948320948209482309842309483209482309482309482309840
        )


class TestNil(TestIdemPotent):
    def test_nil(self):
        self.read_write(None)


class TestBool(TestIdemPotent):
    def test_true(self):
        self.read_write(True)

    def test_false(self):
        self.read_write(False)


class TestArray(TestIdemPotent):
    def test_num_3(self):
        self.read_write([1, 2, 3])

    def test_recursive(self):
        self.read_write([1, 2, 3, [False, None], [42]])


class TestString(TestIdemPotent):
    def test_0(self):
        self.read_write("")

    def test_1(self):
        self.read_write("a")

    def test_5(self):
        self.read_write("abcde")

    def test_unicode(self):
        self.read_write("✓")


class TestHash(TestIdemPotent):
    def test_num_2(self):
        self.read_write({1: 2, 3: 4})

    def test_recursive(self):
        self.read_write({1: 2, 3: 4, 5: [1, 2, 3], 6: {7: 8}, 9: "test"})


class TestFloat(TestIdemPotent):
    def test_num_0(self):
        self.read_write(0.0)

    def test_num_1(self):
        self.read_write(1.0)

    def test_num_1_2(self):
        self.read_write(1.2)

    def test_num__1(self):
        self.read_write(-1.0)

    def test_num_1234567890_123456789(self):
        self.read_write(1234567890.1234567)

    def test_num_inf(self):
        self.read_write(float("inf"))

    def test_num_nan(self):
        self.assertTrue(math.isnan(loads(writes(float("nan")))))

    def test_num__inf(self):
        self.read_write(float("-inf"))


class TestRegexp(TestIdemPotent):
    def test_noflag(self):

        self.assertEqual(b"\x04\bI/\att\x00\x06:\x06EF", writes(re.compile("tt")))
        self.assertEqual(
            b"\x04\bI/\att\x01\x06:\x06EF", writes(re.compile("tt", re.IGNORECASE))
        )

        self.read_write(re.compile("tt"))

    def test_flag(self):
        self.read_write(re.compile("tt", re.IGNORECASE))
        self.read_write(re.compile("tt", re.MULTILINE))


class TestUsrMarshal(TestIdemPotent):
    def test_usr(self):
        a = UsrMarshal("Gem::Version")
        a.marshal_load(["0.1.2"])
        self.read_write(a)


class TestSymbol(TestIdemPotent):
    def test_symbol(self):
        self.read_write("test_symbol")
