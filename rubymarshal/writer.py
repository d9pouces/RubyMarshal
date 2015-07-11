# -*- coding: utf-8 -*-
import re
import struct
import io
from rubymarshal.classes import Symbol, UsrMarshal
from rubymarshal.constants import TYPE_CLASS, TYPE_BIGNUM, TYPE_STRING, TYPE_REGEXP, TYPE_ARRAY, TYPE_HASH, TYPE_STRUCT, TYPE_OBJECT, TYPE_DATA, TYPE_USRMARSHAL, TYPE_NIL, TYPE_TRUE, TYPE_FALSE, \
    TYPE_IVAR, TYPE_LINK, TYPE_SYMLINK, TYPE_SYMBOL, TYPE_FIXNUM
from rubymarshal.constants import TYPE_MODULE
from rubymarshal.constants import TYPE_FLOAT

__author__ = 'Matthieu Gallet'


class Writer(object):
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


    def read(self, token=None):
        if token is None:
            token = self.fd.read(1)
        object_index = None
        if token in (TYPE_CLASS, TYPE_MODULE, TYPE_FLOAT, TYPE_BIGNUM, TYPE_STRING, TYPE_REGEXP, TYPE_ARRAY, TYPE_HASH,
                     TYPE_STRUCT, TYPE_OBJECT, TYPE_DATA, TYPE_USRMARSHAL):
            self.objects.append(None)
            object_index = len(self.objects)
        if token == TYPE_IVAR:
            sub_token = self.fd.read(1)
            content = self.read(sub_token)
            flags = None
            if sub_token == TYPE_REGEXP:
                options = ord(self.fd.read(1))
                flags = 0
                if options & 1:
                    flags |= re.IGNORECASE
                if options & 4:
                    flags |= re.DOTALL
            if sub_token in (TYPE_STRING, TYPE_REGEXP):
                encoding = 'latin1'
                attr_count = self.read_long()
                for x in range(attr_count):
                    attr_name = self.read()
                    attr_value = self.read()
                    if attr_name == Symbol('E') and attr_value is True:
                        encoding = 'utf-8'
                    elif attr_name == Symbol('encoding'):
                        encoding = attr_value.decode('utf-8')
                content = content.decode(encoding)
            else:
                raise ValueError
            if sub_token == TYPE_REGEXP:
                content = re.compile(content, flags)
            result = content
        elif token == TYPE_STRING:
            size = self.read_long()
            result = self.fd.read(size)
        elif token == TYPE_SYMBOL:
            size = self.read_long()
            result = self.fd.read(size)
            result = Symbol(result.decode('utf-8'))
            self.symbols.append(result)
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
            result = float(self.fd.read(size))
        elif token == TYPE_BIGNUM:
            sign = 1 if self.fd.read(1) == b'+' else -1
            num_elements = self.read_long()
            result = 0
            factor = 1
            for x in range(num_elements):
                result += (self.read_short() * factor)
                factor *= 2 ** 16
            result *= sign
        elif token == TYPE_REGEXP:
            size = self.read_long()
            result = self.fd.read(size)
        elif token == TYPE_USRMARSHAL:
            class_name = self.read()
            attr_list = self.read()
            result = UsrMarshal(class_name, attr_list)
        elif token == TYPE_SYMLINK:
            symlink_id = self.read_long()
            result = self.symbols[symlink_id]
        elif token == TYPE_LINK:
            link_id = self.read_long()
            result = self.objects[link_id]
        else:
            raise ValueError
        if object_index is not None:
            self.objects[object_index - 1] = result
        # print('end', result, object_index, self.objects)
        return result

    def write_short(self, obj):
        self.fd.write(struct.pack('<H', obj))

    def write_long(self, obj):
        if obj == 0:
            self.fd.write(b'\x00')
        elif 0 < obj < 123:
            self.fd.write(struct.pack('b', obj + 5))
        elif -124 < obj < 0:
            self.fd.write(struct.pack('b', obj - 5))
        else:
            pass

    def read_long(self):
        s0 = self.fd.read(1)
        if s0 == b'\x00':
            return 0
        l, = struct.unpack('b', s0)
        if 5 < l < 128:
            return l - 5
        elif -129 < l < -5:
            return l + 5
        result = 0
        factor = 1
        for s in range(abs(l)):
            result += (struct.unpack('B', self.fd.read(1))[0] * factor)
            factor *= 256
        if l < 0:
            result = result - factor
        return result


def write(fd, obj):
    fd.write(b'\x04\x08')
    writer = Writer(fd)
    writer.write(obj)


def writes(obj):
    fd = io.BytesIO()
    write(fd, obj)
    return fd.getvalue()
