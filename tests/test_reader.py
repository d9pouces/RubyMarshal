"""
Sample test module corresponding to the :mod:`rubymarshal.sample` module.

A complete documentation can be found at :mod:`unittest`.

"""
import io
import math
import re
import unittest
from unittest.case import TestCase

from rubymarshal.classes import Symbol, UsrMarshal, Module, RubyString, RubyObject
from rubymarshal.reader import loads, load
from rubymarshal.writer import writes

__author__ = "Matthieu Gallet"


class DemoString(RubyObject):
    ruby_class_name = "String"


class DemoDomainError(RubyObject):
    ruby_class_name = "Math::DomainError"


class_mapping = {"String": DemoString, "Math::DomainError": DemoDomainError}


class TestBlog(TestCase):
    """ http://jakegoulding.com/blog/2013/01/15/a-little-dip-into-rubys-marshal-format/ """

    def check(self, a, b):
        b = b.replace(" ", "")
        bytes_array = [4, 8] + [
            int(b[2 * i : 2 * i + 2], 16) for i in range(len(b) // 2)
        ]
        byte_text = bytes(bytes_array)
        fd = io.BytesIO(byte_text)
        bytes_to_obj = load(fd, class_mapping=class_mapping)
        self.assertEqual(a, bytes_to_obj)
        # check that there is no data left
        self.assertEqual(b"", fd.read())
        obj_to_bytes = writes(bytes_to_obj)
        self.assertEqual(byte_text, obj_to_bytes)

    def test_nil(self):
        self.check(None, "30")

    def test_true(self):
        self.check(True, "54")

    def test_false(self):
        self.check(False, "46")

    def test_zero(self):
        self.check(0, "6900")

    def test_one(self):
        self.check(1, "6906")

    def test_array(self):
        self.check([], "5b00")
        self.check([1], "5b06 6906")

    def test_hashes(self):
        self.check({}, "7b00")
        self.check({1: 2}, "7b06 6906 6907")

    def test_symbol(self):
        self.check(Symbol("hello"), "3a0a 6865 6c6c 6f")

    def test_symlinks(self):
        self.check([Symbol("hello"), Symbol("hello")], "5b07 3a0a 6865 6c6c 6f3b 00")

    def test_large_integers(self):
        self.check(123, "6901 7b")
        self.check(256, "6902 0001")
        self.check(2 ** 30 - 1, "6904 ffff ff3f")

    def test_negative_integers(self):
        self.check(-1, "69fa")
        self.check(-124, "69ff 84")
        self.check(-257, " 69fe fffe")
        self.check(-(2 ** 30), "69fc 0000 00c0")

    def test_ivar(self):
        self.check("hello", "4922 0a68 656c 6c6f 063a 0645 54")
        self.check(
            RubyString("hello", {"E": False}), "4922 0a68 656c 6c6f 063a 0645 46"
        )
        self.check(
            RubyString("hello", {"encoding": b"Shift_JIS"}),
            "4922 0a68 656c 6c6f 063a 0d65 6e63 6f64 696e 6722 0e53 6869 6674 5f4a 4953",
        )
        self.check(
            RubyString("hello", {"E": True, "@test": None}),
            "4922 0a68 656c 6c6f 073a 0645 543a 0a40 7465 7374 30",
        )

    def test_raw_strings(self):
        self.check("hello", "4922 0a68 656c 6c6f 063a 0645 54")

    def test_object_links(self):
        self.check(["hello", "hello"], "5b07 4922 0a68 656c 6c6f 063a 0645 5440 06")

    def test_regex(self):
        self.check(re.compile(r"hello"), "492f 0a68 656c 6c6f 0006 3a06 4546")
        self.check(
            re.compile(r"hello", flags=re.IGNORECASE | re.MULTILINE),
            "492f 0a68 656c 6c6f 0506 3a06 4546",
        )

    def test_class(self):
        self.check(DemoDomainError, "6316 4d61 7468 3a3a 446f 6d61 696e 4572 726f 72")
        self.check(DemoString, "630b 5374 7269 6e67")

    def test_modules(self):
        self.check(Module("Enumerable", None), "6d0f 456e 756d 6572 6162 6c65")

    def test_user_object_instances(self):
        self.check(
            RubyObject("DumpTest", {"@a": None}),
            "6f3a 0d44 756d 7054 6573 7406 3a07 4061 30",
        )


class TestLong(TestCase):
    def test_0(self):
        self.assertEqual(loads(b"\x04\bi\x00"), 0)

    def test_1(self):
        self.assertEqual(loads(b"\x04\bi\x06"), 1)

    def test_122(self):
        self.assertEqual(loads(b"\x04\bi\x7F"), 122)

    def test_123(self):
        self.assertEqual(loads(b"\x04\bi\x01{"), 123)

    def test_255(self):
        self.assertEqual(loads(b"\x04\bi\x01\xFF"), 255)

    def test_256(self):
        self.assertEqual(loads(b"\x04\bi\x02\x00\x01"), 256)

    def test_65535(self):
        self.assertEqual(loads(b"\x04\bi\x02\xFF\xFF"), 65535)

    def test_65536(self):
        self.assertEqual(loads(b"\x04\bi\x03\x00\x00\x01"), 65536)

    def test_65537000(self):
        self.assertEqual(loads(b"\x04\bi\x04\xE8\x03\xE8\x03"), 65537000)

    def test__1(self):
        self.assertEqual(loads(b"\x04\bi\xFA"), -1)

    def test__123(self):
        self.assertEqual(loads(b"\x04\bi\x80"), -123)

    def test__124(self):
        self.assertEqual(loads(b"\x04\bi\xFF\x84"), -124)

    def test__256(self):
        self.assertEqual(loads(b"\x04\bi\xFF\x00"), -256)
        self.assertEqual(loads(b"\x04\bi\xFE\x00\xFF"), -256)

    def test__257(self):
        self.assertEqual(loads(b"\x04\bi\xFE\xFF\xFE"), -257)

    def test__259(self):
        self.assertEqual(loads(b"\x04\bi\xFE\xFD\xFE"), -259)

    def test__65536(self):
        self.assertEqual(loads(b"\x04\bi\xFE\x00\x00"), -65536)

    def test__65537(self):
        self.assertEqual(loads(b"\x04\bi\xFD\xFF\xFF\xFE"), -65537)

    def test__65537000(self):
        self.assertEqual(loads(b"\x04\bi\xFC\x18\xFC\x17\xFC"), -65537000)

    def test_long(self):
        self.assertEqual(
            loads(b'\x04\bl+\t\x15\x81\xE9}\xF4\x10"\x11'), 1234567890123456789
        )

    def test_longlong(self):
        self.assertEqual(
            loads(
                b'\x04\bl+\x16\xD0\xE8\xDD\x86T\x9D$\b&\xF83E\xE3\xD2\xFD\xB9"\x12\r\x85"\v\x92\x06\xEF\x7F}/\xB7_\xB7\xEF\xA5)'
            ),
            1234567890123456789012343294802948320948209482309842309483209482309482309482309840,
        )


class TestString(TestCase):
    def test_0(self):
        self.assertEqual(loads(b'\x04\bI"\x00\x06:\x06ET'), "")

    def test_1(self):
        self.assertEqual(loads(b'\x04\bI"\x06a\x06:\x06ET'), "a")

    def test_5(self):
        self.assertEqual(loads(b'\x04\bI"\nabcde\x06:\x06ET'), "abcde")

    def test_utf32(self):
        self.assertEqual(
            loads(
                b'\x04\bI"\x15\x00\x00\xFE\xFF\x00\x00\x00a\x00\x00\x00b\x00\x00\x00c\x06:\rencoding"\vUTF-32'
            ),
            "abc",
        )
        self.assertEqual(
            loads(b'\x04\bI"\r\x00\x00\xFE\xFF\x00\x00\'\x13\x06:\rencoding"\vUTF-32'),
            "✓",
        )

    def test_utf16(self):
        self.assertEqual(
            loads(b'\x04\bI"\r\xFE\xFF\x00a\x00b\x00c\x06:\rencoding"\vUTF-16'), "abc"
        )


class TestNil(TestCase):
    def test_nil(self):
        self.assertEqual(loads(b"\x04\b0"), None)


class TestBool(TestCase):
    def test_true(self):
        self.assertEqual(loads(b"\x04\bT"), True)

    def test_false(self):
        self.assertEqual(loads(b"\x04\bF"), False)


class TestArray(TestCase):
    def test_num_3(self):
        self.assertEqual(loads(b"\x04\b[\bi\x06i\ai\b"), [1, 2, 3])

    def test_recursive(self):
        self.assertEqual(
            loads(b'\x04\b[\ni\x06i\ai\b[\bI"\ttest\x06:\x06ETF0[\x06i/'),
            [1, 2, 3, ["test", False, None], [42]],
        )


class TestHash(TestCase):
    def test_num_2(self):
        self.assertEqual(loads(b"\x04\b{\ai\x06i\ai\bi\t"), {1: 2, 3: 4})

    def test_recursive(self):
        self.assertEqual(
            loads(
                b'\x04\b{\ni\x06i\ai\bi\ti\n[\bi\x06i\ai\bi\v{\x06i\fi\ri\x0EI"\ttest\x06:\x06ET'
            ),
            {1: 2, 3: 4, 5: [1, 2, 3], 6: {7: 8}, 9: "test"},
        )


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
        self.assertEqual(loads(b"\x04\bf\binf"), float("inf"))

    def test_num_nan(self):
        self.assertTrue(math.isnan(loads(b"\x04\bf\bnan")))

    def test_num__inf(self):
        self.assertEqual(loads(b"\x04\bf\t-inf"), float("-inf"))


class TestRegexp(TestCase):
    def test_noflag(self):
        self.assertEqual(loads(b"\x04\bI/\att\x00\x06:\x06EF"), re.compile("tt"))

    def test_flag_1(self):
        self.assertEqual(
            loads(b"\x04\bI/\att\x01\x06:\x06EF"), re.compile("tt", re.IGNORECASE)
        )
        self.assertNotEqual(loads(b"\x04\bI/\att\x01\x06:\x06EF"), re.compile("tt"))

    def test_flag_4(self):
        self.assertEqual(
            loads(b"\x04\bI/\att\x04\x06:\x06EF"), re.compile("tt", re.MULTILINE)
        )
        self.assertNotEqual(loads(b"\x04\bI/\att\x04\x06:\x06EF"), re.compile("tt"))


class TestUsrMarshal(TestCase):
    def test_usr(self):
        a = UsrMarshal(Symbol("Gem::Version"))
        a.marshal_load(["0.1.2"])
        self.assertEqual(loads(b'\x04\bU:\x11Gem::Version[\x06I"\n0.1.2\x06:\x06ET'), a)


class TestSymbol(TestCase):
    def test_symbol(self):
        self.assertEqual(loads(b"\x04\b:\x10test_symbol"), Symbol("test_symbol"))


class TestSymlink(TestCase):
    def test_symlink(self):
        a = Symbol("test_symbol")
        self.assertEqual(loads(b"\x04\b[\a:\x10test_symbol;\x00"), [a, a])


class TestMarshalGemSpec(TestCase):
    """Marshal.load(open("/tmp/raw"))"""

    def double_check(self, bytes_value: bytes):
        fd = io.BytesIO(bytes_value)
        bytes_to_obj = load(fd)
        self.assertEqual(b"", fd.read())
        obj_to_bytes = writes(bytes_to_obj)
        self.assertEqual(bytes_value, obj_to_bytes)

    def test_time(self):
        self.double_check(
            b'\x04\bIu:\tTime\r\xC0\xDB\x1C\xC0\x00\x00\x00\x00\x06:\tzoneI"\bUTC\x06:\x06EF'
        )

    def test_spec(self):
        raw_src = (
            b'\x04\x08u:\x17Gem::Specification\x02*\x01\x04\x08[\x18I"\x0c'
            b'2.5.2.3\x06:\x06ETi\tI"\x06a\x06;\x00TU:\x11Gem::Version['
            b'\x06I"\n0.2.7\x06;\x00TIu:\tTime\r \xa6\x1d\xc0\x00\x00'
            b'\x00\x00\x06:\tzoneI"\x08UTC\x06;\x00FI"\x19a gem generator '
            b'etc.\x06;\x00TU:\x15Gem::Requirement[\x06[\x06[\x07I"\x07>='
            b'\x06;\x00TU;\x06[\x06I"\x060\x06;\x00TU;\t[\x06[\x06[\x07I"'
            b'\x07>=\x06;\x00TU;\x06[\x06I"\x060\x06;\x00TI"\truby\x06;'
            b'\x00T[\x000I"\x13degcat@126.com\x06;\x00T[\x06I"\x0bauthor'
            b'\x06;\x00T0I"\x1fhttps://github.com/axgle/a\x06;\x00TT@\x1e'
            b'[\x06I"\x08MIT\x06;\x00T{\x00'
        )
        self.double_check(raw_src)

    def test_subgem_spec(self):
        raw_src = (
            b'\x04\x08[\x18I"\n2.2.2\x06:\x06ETi\tI"\x14capistrano-demo\x06;\x00'
            b'TU:\x11Gem::Version[\x06I"\n0.0.5\x06;\x00TIu:\tTime\r\xc0\xdb\x1c'
            b'\xc0\x00\x00\x00\x00\x06:\tzoneI"\x08UTC\x06;\x00FI"$Create demo-h'
            b"ost by branch name\x06;\x00TU:\x15Gem::Requirement[\x06[\x06[\x07I"
            b'"\x07>=\x06;\x00TU;\x06[\x06I"\x060\x06;\x00TU;\t[\x06[\x06[\x07I"'
            b'\x07>=\x06;\x00TU;\x06[\x06I"\x060\x06;\x00TI"\truby\x06;\x00T[\to'
            b':\x14Gem::Dependency\n:\n@nameI"\x0fcapistrano\x06;\x00T:\x11@requ'
            b'irementU;\t[\x06[\x06[\x07I"\x07~>\x06;\x00TU;\x06[\x06I"\x083.1'
            b"\x06;\x00T:\n@type:\x0cruntime:\x10@prereleaseF:\x1a@version_requi"
            b'rementsU;\t[\x06[\x06[\x07I"\x07~>\x06;\x00TU;\x06[\x06I"\x083.1'
            b'\x06;\x00To;\n\n;\x0bI"\x0cbundler\x06;\x00T;\x0cU;\t[\x06[\x06['
            b'\x07I"\x07~>\x06;\x00TU;\x06[\x06I"\x0b1.10.0\x06;\x00T;\r:\x10dev'
            b'elopment;\x0fF;\x10U;\t[\x06[\x06[\x07I"\x07~>\x06;\x00TU;\x06['
            b'\x06I"\x0b1.10.0\x06;\x00To;\n\n;\x0bI"\trake\x06;\x00T;\x0cU;\t['
            b'\x06[\x06[\x07I"\x07>=\x06;\x00TU;\x06[\x06I"\x060\x06;\x00T;\r;'
            b'\x11;\x0fF;\x10U;\t[\x06[\x06[\x07I"\x07>=\x06;\x00TU;\x06[\x06I"'
            b'\x060\x06;\x00To;\n\n;\x0bI"\nrspec\x06;\x00T;\x0cU;\t[\x06[\x06['
            b'\x07I"\x07~>\x06;\x00TU;\x06[\x06I"\n3.2.0\x06;\x00T;\r;\x11;\x0f'
            b'F;\x10U;\t[\x06[\x06[\x07I"\x07~>\x06;\x00TU;\x06[\x06I"\n3.2.0'
            b'\x06;\x00T0[\x06I"\x1farthur.shcheglov@gmail.com\x06;\x00T[\x06I"'
            b'\x1fArthur Shcheglov (fc_arny)\x06;\x00TI"$Create demo-host by br'
            b'anch name\x06;\x00TI"\x1chttp://at-consulting.ru\x06;\x00TT@\x1e['
            b'\x06I"\x08MIT\x06;\x00T{\x00'
        )
        actual_obj = loads(raw_src)
        raw_dst = writes(actual_obj)
        # print(raw_dst)
        dst_obj = loads(raw_dst)
        self.assertEqual(actual_obj, dst_obj)
        # print(dst_obj, actual_obj == dst_obj)
        # loads(raw_dst)
        self.assertEqual(raw_src, raw_dst)

    def test_gem_spec(self):
        raw_src = (
            b'\x04\x08u:\x17Gem::Specification\x02d\x03\x04\x08[\x18I"\n2.2.2\x06:\x06ETi'
            b'\tI"\x14capistrano-demo\x06;\x00TU:\x11Gem::Version[\x06I"\n0.0.5\x06;\x00TIu:'
            b'\tTime\r\xc0\xdb\x1c\xc0\x00\x00\x00\x00\x06:\tzoneI"\x08UTC\x06;\x00FI"$'
            b"Create demo-host by branch name\x06;\x00TU:\x15Gem::Requirement[\x06[\x06[\x07"
            b'I"\x07>=\x06;\x00TU;\x06[\x06I"\x060\x06;\x00TU;\t[\x06[\x06[\x07I"\x07>=\x06;'
            b'\x00TU;\x06[\x06I"\x060\x06;\x00TI"\truby\x06;\x00T[\to:\x14Gem::Dependency\n:\n'
            b'@nameI"\x0fcapistrano\x06;\x00T:\x11@requirementU;\t[\x06[\x06[\x07I"\x07~>\x06;\x00'
            b'TU;\x06[\x06I"\x083.1\x06;\x00T:\n@type:\x0cruntime:\x10@prereleaseF:\x1a'
            b'@version_requirementsU;\t[\x06[\x06[\x07I"\x07~>\x06;\x00TU;\x06[\x06I"\x083.1\x06;\x00'
            b'To;\n\n;\x0bI"\x0cbundler\x06;\x00T;\x0cU;\t[\x06[\x06[\x07I"\x07~>\x06;\x00TU;\x06[\x06'
            b'I"\x0b1.10.0\x06;\x00T;\r:\x10development;\x0fF;\x10U;\t[\x06[\x06[\x07I"\x07~>\x06;\x00'
            b'TU;\x06[\x06I"\x0b1.10.0\x06;\x00To;\n\n;\x0bI"\trake\x06;\x00T;\x0cU;\t[\x06[\x06[\x07'
            b'I"\x07>=\x06;\x00TU;\x06[\x06I"\x060\x06;\x00T;\r;\x11;\x0fF;\x10U;\t[\x06[\x06[\x07'
            b'I"\x07>=\x06;\x00TU;\x06[\x06I"\x060\x06;\x00To;\n\n;\x0bI"\nrspec\x06;\x00T;\x0cU;\t'
            b'[\x06[\x06[\x07I"\x07~>\x06;\x00TU;\x06[\x06I"\n3.2.0\x06;\x00T;\r;\x11;\x0fF;\x10U;\t'
            b'[\x06[\x06[\x07I"\x07~>\x06;\x00TU;\x06[\x06I"\n3.2.0\x06;\x00T0[\x06I"\x1farthur.shcheg'
            b'lov@gmail.com\x06;\x00T[\x06I"\x1fArthur Shcheglov (fc_arny)\x06;\x00TI"$Create demo-host '
            b'by branch name\x06;\x00TI"\x1chttp://at-consulting.ru\x06;\x00TT@\x1e[\x06I"\x08MIT\x06;\x00T{\x00'
        )
        actual_obj = loads(raw_src)
        raw_dst = writes(actual_obj)
        dst_obj = loads(raw_dst)
        self.assertEqual(actual_obj, dst_obj)
        self.assertEqual(raw_src, raw_dst)


class TestLink(TestCase):
    def test_link_base(self):
        a = [1, 2, 3]
        result = loads(b"\x04\b[\b[\bi\x06i\ai\b@\x06@\x06")
        self.assertEqual(result, [a, a, a])
        result[0][2] = 4
        self.assertEqual(result[1][2], 4)
        self.assertEqual(result[2][2], 4)

    def test_link_usr(self):
        a = UsrMarshal(Symbol("Gem::Version"))
        a.marshal_load(["0.1.2"])
        result = loads(b'\x04\b[\aU:\x11Gem::Version[\x06I"\n0.1.2\x06:\x06ET@\x06')
        self.assertEqual(result, [a, a])

    def test_link_usr_base(self):
        a = [1, 2, 3]
        b = UsrMarshal(Symbol("Gem::Version"))
        b.marshal_load(["0.1.2"])
        result = loads(
            b'\x04\b[\b[\a[\bi\x06i\ai\b@\a[\aU:\x11Gem::Version[\x06I"\n0.1.2\x06:\x06ET@\t[\a@\a@\a'
        )
        self.assertEqual(result, [[a, a], [b, b], [a, a]])


if __name__ == "__main__":
    unittest.main()
