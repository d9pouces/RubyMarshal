from unittest import TestCase
import io
from rubymarshal.utils import (
    write_ubyte,
    write_sbyte,
    write_ushort,
    read_ushort,
    read_sbyte,
    read_ubyte,
)

__author__ = "Matthieu Gallet"


class Test(TestCase):
    def check_write(self, fn, obj):
        fd = io.BytesIO()
        fn(fd, obj)
        return fd.getvalue()

    def check_read(self, fn, content):
        fd = io.BytesIO(content)
        return fn(fd)

    def test_write_ushort(self):
        content = self.check_write(write_ushort, 1)
        self.assertEqual(b"\x01\x00", content)

    def test_write_sbyte(self):
        content = self.check_write(write_sbyte, 1)
        self.assertEqual(b"\x01", content)
        content = self.check_write(write_sbyte, -1)
        self.assertEqual(b"\xff", content)

    def test_write_ubyte(self):
        content = self.check_write(write_ubyte, 1)
        self.assertEqual(b"\x01", content)
        content = self.check_write(write_ubyte, 255)
        self.assertEqual(b"\xff", content)

    def test_read_ushort(self):
        content = self.check_read(read_ushort, b"\x01\x00")
        self.assertEqual(1, content)

    def test_read_sbyte(self):
        content = self.check_read(read_sbyte, b"\x01")
        self.assertEqual(1, content)
        content = self.check_read(read_sbyte, b"\xff")
        self.assertEqual(-1, content)

    def test_read_ubyte(self):
        content = self.check_read(read_ubyte, b"\x01")
        self.assertEqual(1, content)
        content = self.check_read(read_ubyte, b"\xff")
        self.assertEqual(255, content)


#
