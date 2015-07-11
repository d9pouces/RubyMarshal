# -*- coding: utf-8 -*-
from unittest import TestCase
import io
from rubymarshal.writer import Writer

__author__ = 'Matthieu Gallet'


def write(obj):
    fd = io.BytesIO()
    writer = Writer(fd)
    writer.write_long(obj)
    return fd.getvalue()


class TestWriteLong(TestCase):
    def test_0(self):
        self.assertEqual(b'\x00', write(0))

    def test_1(self):
        self.assertEqual(b'\x06', write(1))

    def test_122(self):
        self.assertEqual(b'\x7F', write(122))

    def test_123(self):
        self.assertEqual(b'\x01{', write(123))

    def test_255(self):
        self.assertEqual(b'\x01\xFF', write(255))

    def test_256(self):
        self.assertEqual(b'\x02\x00\x01', write(256))

    def test_65535(self):
        self.assertEqual(b'\x02\xFF\xFF', write(65535))

    def test_65536(self):
        self.assertEqual(b'\x03\x00\x00\x01', write(65536))

    def test_65537000(self):
        self.assertEqual(b"\x04\xE8\x03\xE8\x03", write(65537000))

    def test__1(self):
        self.assertEqual(b'\xFA', write(-1))

    def test__123(self):
        self.assertEqual(b'\x80', write(-123))

    def test__124(self):
        self.assertEqual(b'\xFF\x84', write(-124))

    def test__256(self):
        self.assertEqual(b'\xFF\x00', write(-256))

    def test__257(self):
        self.assertEqual(b'\xFE\xFF\xFE', write(-257))

    def test__259(self):
        self.assertEqual(b"\xFE\xFD\xFE", write(-259))

    def test__65536(self):
        self.assertEqual(b'\xFE\x00\x00', write(-65536))

    def test__65537(self):
        self.assertEqual(b'\xFD\xFF\xFF\xFE', write(-65537))

    def test__65537000(self):
        self.assertEqual(b"\xFC\x18\xFC\x17\xFC", write(-65537000))
