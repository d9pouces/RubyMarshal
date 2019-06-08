import io
import math
import re

from rubymarshal.classes import (
    Symbol,
    UsrMarshal,
    UserDef,
    RubyString,
    Module,
    RubyObject,
)
from rubymarshal.constants import (
    TYPE_BIGNUM,
    TYPE_STRING,
    TYPE_REGEXP,
    TYPE_ARRAY,
    TYPE_HASH,
    TYPE_USRMARSHAL,
    TYPE_NIL,
    TYPE_TRUE,
    TYPE_FALSE,
    TYPE_IVAR,
    TYPE_LINK,
    TYPE_SYMLINK,
    TYPE_SYMBOL,
    TYPE_FIXNUM,
    TYPE_USERDEF,
    TYPE_CLASS,
    TYPE_MODULE,
    TYPE_OBJECT,
)
from rubymarshal.constants import TYPE_FLOAT
from rubymarshal.utils import write_ushort, write_sbyte, write_ubyte

__author__ = "Matthieu Gallet"

re_class = re.compile("").__class__
simple_float_re = re.compile(r"^\d+\.\d*0+$")


class Writer:
    def __init__(self, fd):
        self.symbols = {}
        self.objects = {}
        self.fd = fd

    def write(self, obj):
        if obj is None:
            self.fd.write(TYPE_NIL)
        elif obj is False:
            self.fd.write(TYPE_FALSE)
        elif obj is True:
            self.fd.write(TYPE_TRUE)
        elif isinstance(obj, int):
            if obj.bit_length() <= 5 * 8:
                self.fd.write(TYPE_FIXNUM)
                # noinspection PyTypeChecker
                self.write_long(obj)
            else:
                self.fd.write(TYPE_BIGNUM)
                if obj < 0:
                    self.fd.write(b"-")
                else:
                    self.fd.write(b"+")
                obj = abs(obj)
                size = int(math.ceil(obj.bit_length() / 16.0))
                self.write_long(size)
                for i in range(size):
                    self.write_short(obj % 65536)
                    obj //= 65536
        elif isinstance(obj, Symbol):
            if obj.name in self.symbols:
                self.fd.write(TYPE_SYMLINK)
                self.write_long(self.symbols[obj.name])
            else:
                self.fd.write(TYPE_SYMBOL)
                symbol_index = len(self.symbols)
                self.symbols[obj.name] = symbol_index
                encoded = obj.name.encode("utf-8")
                self.write_long(len(encoded))
                self.fd.write(encoded)
        elif isinstance(obj, list):
            if self.must_write(obj):
                self.fd.write(TYPE_ARRAY)
                self.write_long(len(obj))
                for x in obj:
                    self.write(x)
        elif isinstance(obj, dict):
            if self.must_write(obj):
                self.fd.write(TYPE_HASH)
                self.write_long(len(obj))
                for key, value in obj.items():
                    self.write(key)
                    self.write(value)
        elif isinstance(obj, bytes):
            self.fd.write(TYPE_STRING)
            self.write_long(len(obj))
            self.fd.write(obj)
        elif isinstance(obj, str):
            obj = obj.encode("utf-8")
            self.fd.write(TYPE_IVAR)
            self.fd.write(TYPE_STRING)
            self.write_long(len(obj))
            self.fd.write(obj)
            self.write_long(1)
            self.write(Symbol("E"))
            self.write(True)
        elif isinstance(obj, RubyString):
            if self.must_write(obj):
                encoding = "utf-8"
                attributes = obj.attributes
                if "E" in attributes and not attributes["E"]:
                    encoding = "latin-1"
                elif "encoding" in attributes:
                    encoding = attributes["encoding"].decode()
                else:
                    attributes["E"] = True
                encoded = obj.encode(encoding)
                self.fd.write(TYPE_IVAR)
                self.fd.write(TYPE_STRING)
                self.write_long(len(encoded))
                self.fd.write(encoded)
                self.write_attributes(attributes)
        elif isinstance(obj, float):
            obj = "%.20g" % obj
            if simple_float_re.match(obj):
                while obj.endswith("0"):
                    obj = obj[:-1]
            obj = obj.encode("utf-8")
            self.fd.write(TYPE_FLOAT)
            self.write_long(len(obj))
            self.fd.write(obj)
        elif isinstance(obj, re_class):
            flags = 0
            if obj.flags & re.IGNORECASE:
                flags += 1
            if obj.flags & re.MULTILINE:
                flags += 4
            self.fd.write(TYPE_IVAR)
            self.fd.write(TYPE_REGEXP)
            pattern = obj.pattern.encode("utf-8")
            self.write_long(len(pattern))
            self.fd.write(pattern)
            write_ubyte(self.fd, flags)
            self.write_long(1)
            self.write(Symbol("E"))
            self.write(False)
        elif isinstance(obj, Module):
            self.fd.write(TYPE_MODULE)
            self.write_long(len(obj.ruby_class_name.encode()))
            self.fd.write(obj.ruby_class_name.encode())
        elif isinstance(obj, UsrMarshal):
            if self.must_write(obj):
                self.fd.write(TYPE_USRMARSHAL)
                self.write(Symbol(obj.ruby_class_name))
                obj_attributes = obj.attributes
                self.write(obj_attributes)
        elif isinstance(obj, UserDef):
            if self.must_write(obj):
                if obj.attributes:
                    self.fd.write(TYPE_IVAR)
                self.fd.write(TYPE_USERDEF)
                name = obj.ruby_class_name
                if isinstance(name, Symbol):
                    self.write(name)
                else:
                    encoded = name.encode("utf-8")
                    self.write_long(len(encoded))
                    self.fd.write(encoded)
                # noinspection PyProtectedMember
                bdata = obj._dump()
                self.write_long(len(bdata))
                self.fd.write(bdata)
                if obj.attributes:
                    self.write_attributes(obj.attributes)
        elif isinstance(obj, RubyObject):
            if self.must_write(obj):
                self.fd.write(TYPE_OBJECT)
                self.write(Symbol(obj.ruby_class_name))
                if not isinstance(obj.attributes, dict):
                    raise ValueError("%r values is not a dict" % obj)
                self.write_attributes(obj.attributes)
        elif isinstance(obj, type) and issubclass(obj, RubyObject):
            self.fd.write(TYPE_CLASS)
            self.write_long(len(obj.ruby_class_name.encode()))
            self.fd.write(obj.ruby_class_name.encode())
        else:
            raise ValueError(
                "unmarshable object: %s(%r)" % (obj.__class__.__name__, obj)
            )

    def write_attributes(self, attributes):
        self.write_long(len(attributes))
        for attr_name, attr_value in attributes.items():
            self.write(Symbol(attr_name))
            self.write(attr_value)

    def show(self, size=10, prefix="->"):
        pos = self.fd.tell()
        new_pos = max(0, pos - size)
        self.fd.seek(new_pos)
        print("%s %r" % (prefix, self.fd.read(pos - new_pos)))
        self.fd.seek(pos)

    def write_short(self, obj):
        write_ushort(self.fd, obj)

    def write_long(self, obj):
        if obj == 0:
            self.fd.write(b"\0")
        elif 0 < obj < 123:
            write_sbyte(self.fd, obj + 5)
        elif -124 < obj < 0:
            write_sbyte(self.fd, obj - 5)
        else:
            size = int(math.ceil(obj.bit_length() / 8.0))
            if size > 5:
                raise ValueError("%d too long for serialization" % obj)
            original_obj = obj
            factor = 256 ** size
            if obj < 0 and obj == -factor:
                size -= 1
                obj += factor / 256
            elif obj < 0:
                obj += factor
            sign = int(math.copysign(size, original_obj))
            write_sbyte(self.fd, sign)
            for i in range(size):
                write_ubyte(self.fd, obj % 256)
                obj //= 256

    def must_write(self, obj):
        if id(obj) in self.objects:
            self.fd.write(TYPE_LINK)
            self.write_long(self.objects[id(obj)])
            return False
        else:
            link_index = len(self.objects)
            self.objects[id(obj)] = link_index
            return True


def write(fd, obj):
    fd.write(b"\x04\x08")
    writer = Writer(fd)
    writer.write(obj)


def writes(obj):
    fd = io.BytesIO()
    write(fd, obj)
    return fd.getvalue()
