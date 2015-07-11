# -*- coding: utf-8 -*-
"""
Sample test module corresponding to the :mod:`rubymarshal.sample` module.

A complete documentation can be found at :mod:`unittest`.

"""

from __future__ import unicode_literals
import re
import unittest
from unittest.case import TestCase
import math

from rubymarshal.classes import Symbol, UsrMarshal
from rubymarshal.reader import loads

__author__ = 'Matthieu Gallet'


class TestLong(TestCase):

    def test_0(self):
        self.assertEqual(loads(b'\x04\bi\x00'), 0)

    def test_1(self):
        self.assertEqual(loads(b'\x04\bi\x06'), 1)

    def test_122(self):
        self.assertEqual(loads(b'\x04\bi\x7F'), 122)

    def test_123(self):
        self.assertEqual(loads(b'\x04\bi\x01{'), 123)

    def test_255(self):
        self.assertEqual(loads(b'\x04\bi\x01\xFF'), 255)

    def test_256(self):
        self.assertEqual(loads(b'\x04\bi\x02\x00\x01'), 256)

    def test_65535(self):
        self.assertEqual(loads(b'\x04\bi\x02\xFF\xFF'), 65535)

    def test_65536(self):
        self.assertEqual(loads(b'\x04\bi\x03\x00\x00\x01'), 65536)

    def test_65537000(self):
        self.assertEqual(loads(b"\x04\bi\x04\xE8\x03\xE8\x03"), 65537000)

    def test__1(self):
        self.assertEqual(loads(b'\x04\bi\xFA'), -1)

    def test__123(self):
        self.assertEqual(loads(b'\x04\bi\x80'), -123)

    def test__124(self):
        self.assertEqual(loads(b'\x04\bi\xFF\x84'), -124)

    def test__256(self):
        self.assertEqual(loads(b'\x04\bi\xFF\x00'), -256)
        self.assertEqual(loads(b'\x04\bi\xFE\x00\xFF'), -256)

    def test__257(self):
        self.assertEqual(loads(b'\x04\bi\xFE\xFF\xFE'), -257)

    def test__259(self):
        self.assertEqual(loads(b"\x04\bi\xFE\xFD\xFE"), -259)

    def test__65536(self):
        self.assertEqual(loads(b'\x04\bi\xFE\x00\x00'), -65536)

    def test__65537(self):
        self.assertEqual(loads(b'\x04\bi\xFD\xFF\xFF\xFE'), -65537)

    def test__65537000(self):
        self.assertEqual(loads(b"\x04\bi\xFC\x18\xFC\x17\xFC"), -65537000)

    def test_long(self):
        self.assertEqual(loads(b"\x04\bl+\t\x15\x81\xE9}\xF4\x10\"\x11"), 1234567890123456789)

    def test_longlong(self):
        self.assertEqual(loads(b"\x04\bl+\x16\xD0\xE8\xDD\x86T\x9D$\b&\xF83E\xE3\xD2\xFD\xB9\"\x12\r\x85\"\v\x92\x06\xEF\x7F}/\xB7_\xB7\xEF\xA5)"),
                         1234567890123456789012343294802948320948209482309842309483209482309482309482309840)


class TestString(TestCase):

    def test_0(self):
        self.assertEqual(loads(b'\x04\bI\"\x00\x06:\x06ET'), '')

    def test_1(self):
        self.assertEqual(loads(b'\x04\bI\"\x06a\x06:\x06ET'), 'a')

    def test_5(self):
        self.assertEqual(loads(b'\x04\bI\"\nabcde\x06:\x06ET'), 'abcde')

    def test_utf32(self):
        self.assertEqual(loads(b"\x04\bI\"\x15\x00\x00\xFE\xFF\x00\x00\x00a\x00\x00\x00b\x00\x00\x00c\x06:\rencoding\"\vUTF-32"),  "abc")
        self.assertEqual(loads(b"\x04\bI\"\r\x00\x00\xFE\xFF\x00\x00'\x13\x06:\rencoding\"\vUTF-32"), '✓')

    def test_utf16(self):
        self.assertEqual(loads(b"\x04\bI\"\r\xFE\xFF\x00a\x00b\x00c\x06:\rencoding\"\vUTF-16"),  "abc")


class TestNil(TestCase):

    def test_nil(self):
        self.assertEqual(loads(b'\x04\b0'), None)


class TestBool(TestCase):

    def test_true(self):
        self.assertEqual(loads(b'\x04\bT'), True)

    def test_false(self):
        self.assertEqual(loads(b'\x04\bF'), False)


class TestArray(TestCase):

    def test_num_3(self):
        self.assertEqual(loads(b"\x04\b[\bi\x06i\ai\b"), [1, 2, 3])

    def test_recursive(self):
        self.assertEqual(loads(b"\x04\b[\ni\x06i\ai\b[\bI\"\ttest\x06:\x06ETF0[\x06i/"), [1, 2, 3, ["test", False, None], [42]])


class TestHash(TestCase):

    def test_num_2(self):
        self.assertEqual(loads(b"\x04\b{\ai\x06i\ai\bi\t"), {1: 2, 3: 4})

    def test_recursive(self):
        self.assertEqual(loads(b"\x04\b{\ni\x06i\ai\bi\ti\n[\bi\x06i\ai\bi\v{\x06i\fi\ri\x0EI\"\ttest\x06:\x06ET"),
                         {1: 2, 3: 4, 5: [1, 2, 3], 6: {7: 8}, 9: "test"})


class TestFloat(TestCase):

    def test_num_0(self):
        self.assertEqual(loads(b"\x04\bf\x060"), 0.0)

    def test_num_1(self):
        self.assertEqual(loads(b"\x04\bf\x061"), 1.0)

    def test_num_1_2(self):
        self.assertEqual(loads(b"\x04\bf\b1.2"), 1.2)

    def test_num__1(self):
        self.assertEqual(loads(b"\x04\bf\a-1"), -1.0)

    def test_num_1234567890_123456789(self):
        self.assertEqual(loads(b"\x04\bf\x171234567890.1234567"), 1234567890.1234567)

    def test_num_inf(self):
        self.assertEqual(loads(b"\x04\bf\binf"), float('inf'))

    def test_num_nan(self):

        self.assertTrue(math.isnan(loads(b"\x04\bf\bnan")))

    def test_num__inf(self):
        self.assertEqual(loads(b"\x04\bf\t-inf"), float('-inf'))


class TestRegexp(TestCase):
    def test_noflag(self):
        self.assertEqual(loads(b"\x04\bI/\att\x00\x06:\x06EF"), re.compile('tt'))

    def test_flag_1(self):
        self.assertEqual(loads(b"\x04\bI/\att\x01\x06:\x06EF"), re.compile('tt', re.IGNORECASE))
        self.assertNotEqual(loads(b"\x04\bI/\att\x01\x06:\x06EF"), re.compile('tt'))

    def test_flag_4(self):
        self.assertEqual(loads(b"\x04\bI/\att\x04\x06:\x06EF"), re.compile('tt', re.DOTALL))
        self.assertNotEqual(loads(b"\x04\bI/\att\x04\x06:\x06EF"), re.compile('tt'))


class TestUsrMarshal(TestCase):

    def test_usr(self):
        a = UsrMarshal('Gem::Version', ['0.1.2'])
        self.assertEqual(loads(b"\x04\bU:\x11Gem::Version[\x06I\"\n0.1.2\x06:\x06ET"), a)


class TestSymbol(TestCase):
    def test_symbol(self):
        self.assertEqual(loads(b"\x04\b:\x10test_symbol"), Symbol('test_symbol'))


class TestSymlink(TestCase):
    def test_symlink(self):
        a = Symbol('test_symbol')
        self.assertEqual(loads(b"\x04\b[\a:\x10test_symbol;\x00"), [a, a])


class TestLink(TestCase):

    def test_link_base(self):
        a = [1, 2, 3]
        result = loads(b"\x04\b[\b[\bi\x06i\ai\b@\x06@\x06")
        self.assertEqual(result, [a, a, a])
        result[0][2] = 4
        self.assertEqual(result[1][2], 4)
        self.assertEqual(result[2][2], 4)

    def test_link_usr(self):
        a = UsrMarshal('Gem::Version', ['0.1.2'])
        result = loads(b"\x04\b[\aU:\x11Gem::Version[\x06I\"\n0.1.2\x06:\x06ET@\x06")
        self.assertEqual(result, [a, a])

    def test_link_usr_base(self):
        a = [1, 2, 3]
        b = UsrMarshal('Gem::Version', ['0.1.2'])
        result = loads(b"\x04\b[\b[\a[\bi\x06i\ai\b@\a[\aU:\x11Gem::Version[\x06I\"\n0.1.2\x06:\x06ET@\t[\a@\a@\a")
        self.assertEqual(result, [[a, a], [b, b], [a, a]])

if __name__ == '__main__':
    unittest.main()
