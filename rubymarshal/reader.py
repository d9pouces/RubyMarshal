import io
import re

from rubymarshal.classes import (
    UsrMarshal,
    Symbol,
    UserDef,
    Extended,
    Object,
    Module,
    String, Class)
from rubymarshal.constants import (
    TYPE_NIL,
    TYPE_TRUE,
    TYPE_FALSE,
    TYPE_FIXNUM,
    TYPE_IVAR,
    TYPE_STRING,
    TYPE_SYMBOL,
    TYPE_ARRAY,
    TYPE_HASH,
    TYPE_FLOAT,
    TYPE_BIGNUM,
    TYPE_REGEXP,
    TYPE_USRMARSHAL,
    TYPE_SYMLINK,
    TYPE_LINK,
    TYPE_DATA,
    TYPE_OBJECT,
    TYPE_STRUCT,
    TYPE_MODULE,
    TYPE_CLASS,
    TYPE_USERDEF,
    TYPE_EXTENDED,
)
from rubymarshal.utils import read_ushort, read_sbyte, read_ubyte

__author__ = "Matthieu Gallet"


class Reader:
    def __init__(self, fd, usr_marshal_mapping=None, userdef_mapping=None):
        self.symbols = []
        self.objects = []
        self.fd = fd
        self.usr_marshal_mapping = usr_marshal_mapping or {}
        self.userdef_mapping = userdef_mapping or {}

    def read(self, token=None, ivar=False):
        if token is None:
            token = self.fd.read(1)
        object_index = None
        if token in (
            TYPE_IVAR,
            # TYPE_EXTENDED, TYPE_UCLASS, ????
            TYPE_CLASS,
            TYPE_MODULE,
            TYPE_FLOAT,
            TYPE_BIGNUM,
            TYPE_REGEXP,
            TYPE_ARRAY,
            TYPE_HASH,
            TYPE_STRUCT,
            TYPE_OBJECT,
            TYPE_DATA,
            TYPE_USRMARSHAL,
        ):
            self.objects.append(None)
            object_index = len(self.objects)
        if token == TYPE_NIL:
            result = None
        elif token == TYPE_TRUE:
            result = True
        elif token == TYPE_FALSE:
            result = False
        elif token == TYPE_IVAR:
            sub_token = self.fd.read(1)
            content = self.read(sub_token, ivar=True)
            flags = None
            if sub_token == TYPE_REGEXP:
                options = ord(self.fd.read(1))
                flags = 0
                if options & 1:
                    flags |= re.IGNORECASE
                if options & 4:
                    flags |= re.MULTILINE
            if sub_token in (TYPE_STRING, TYPE_REGEXP, TYPE_USERDEF):
                encoding = "latin1"
                attr_count = self.read_long()
                attrs = {}
                for x in range(attr_count):
                    attr_name = self.read()
                    attr_value = self.read()
                    if attr_name == Symbol("E") and attr_value is True:
                        encoding = "utf-8"
                    elif attr_name == Symbol("encoding"):
                        attr_value = attr_value.decode("utf-8")
                        encoding = attr_value
                    attrs[attr_name] = attr_value
                if sub_token in (TYPE_STRING, TYPE_REGEXP):
                    content = content.decode(encoding)
                # string instance attributes are discarded
                if attrs:
                    content = String(content, attrs)
            else:
                raise ValueError
            if sub_token == TYPE_REGEXP:
                content = re.compile(str(content), flags)
            result = content
        elif token == TYPE_STRING:
            size = self.read_long()
            result = self.fd.read(size)
        elif token == TYPE_SYMBOL:
            result = self.read_symreal()
        elif token == TYPE_FIXNUM:
            result = self.read_long()
        elif token == TYPE_ARRAY:
            num_elements = self.read_long()
            # noinspection PyUnusedLocal
            result = [self.read() for x in range(num_elements)]
        elif token == TYPE_HASH:
            num_elements = self.read_long()
            result = {}
            for x in range(num_elements):
                key = self.read()
                value = self.read()
                result[key] = value
            result = result
        elif token == TYPE_FLOAT:
            size = self.read_long()
            result = float(self.fd.read(size).decode("utf-8"))
        elif token == TYPE_BIGNUM:
            sign = 1 if self.fd.read(1) == b"+" else -1
            num_elements = self.read_long()
            result = 0
            factor = 1
            for x in range(num_elements):
                result += self.read_short() * factor
                factor *= 2 ** 16
            result *= sign
        elif token == TYPE_REGEXP:
            size = self.read_long()
            result = self.fd.read(size)
        elif token == TYPE_USRMARSHAL:
            class_name = self.read()
            attr_list = self.read()
            cls = self.usr_marshal_mapping.get(class_name, UsrMarshal)
            result = cls(class_name, attr_list)
        elif token == TYPE_SYMLINK:
            result = self.read_symlink()
        elif token == TYPE_LINK:
            link_id = self.read_long()
            result = self.objects[link_id]
        elif token == TYPE_USERDEF:
            class_name = self.read()
            data = self.read(TYPE_STRING)
            if not ivar:
                data = loads(data)
            result = UserDef(Symbol(class_name), data)
        elif token == TYPE_MODULE:
            data = self.read(TYPE_STRING)
            module_name = data.decode()
            result = Module(module_name, None)
        elif token == TYPE_OBJECT:
            class_name = self.read()
            attr_count = self.read_long()
            # noinspection PyUnusedLocal
            attrs = {}
            for index in range(attr_count):
                key = self.read()
                value = self.read()
                attrs[key] = value
            # if not ivar:
            #     data = self.read()
            result = Object(class_name, attrs)
        elif token == TYPE_EXTENDED:
            class_name = self.read(TYPE_STRING)
            result = Extended(class_name, None)
        elif token == TYPE_CLASS:
            data = self.read(TYPE_STRING)
            class_name = data.decode()
            result = Class(class_name, None)
        else:
            raise ValueError("token %s is not recognized" % token)
        if object_index is not None:
            self.objects[object_index - 1] = result
        return result

    def read_short(self):
        return read_ushort(self.fd)

    def read_long(self):
        length = read_sbyte(self.fd)
        if length == 0:
            return 0
        if 5 < length < 128:
            return length - 5
        elif -129 < length < -5:
            return length + 5
        result = 0
        factor = 1
        for s in range(abs(length)):
            result += read_ubyte(self.fd) * factor
            factor *= 256
        if length < 0:
            result = result - factor
        return result

    def read_symbol(self):
        ivar = 0
        while True:
            token = self.fd.read(1)
            if token == TYPE_IVAR:
                ivar = 1
                continue
            elif token == TYPE_SYMBOL:
                return self.read_symreal()
            elif token == TYPE_SYMLINK:
                if ivar:
                    raise ValueError("dump format error (symlink with encoding)")
                return self.read_symlink()
            raise ValueError("error while reading symbol with token %r" % token)

    def read_symlink(self):
        symlink_id = self.read_long()
        return self.symbols[symlink_id]

    def read_symreal(self):
        size = self.read_long()
        result = self.fd.read(size)
        result = Symbol(result.decode("utf-8"))
        self.symbols.append(result)
        return result


def load(fd):
    assert fd.read(1) == b"\x04"
    assert fd.read(1) == b"\x08"

    loader = Reader(fd)
    return loader.read()


def loads(byte_text):
    return load(io.BytesIO(byte_text))
