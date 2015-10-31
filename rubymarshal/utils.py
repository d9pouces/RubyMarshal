# -*- coding: utf-8 -*-
"""regroup all struct functions and some compatibility tricks for Python2/3.

Do not import unicode_literals from __future__.
"""
import sys
import struct

__author__ = 'Matthieu Gallet'

# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    integer_types = int,
    text_type = str
    binary_type = bytes
else:
    # noinspection PyUnresolvedReferences
    integer_types = (int, long)
    # noinspection PyUnresolvedReferences
    text_type = unicode
    binary_type = str


def write_ushort(fd, obj):
    fd.write(struct.pack('<H', obj))


def write_sbyte(fd, obj):
    fd.write(struct.pack('b', obj))


def write_ubyte(fd, obj):
    fd.write(struct.pack('B', obj))


def read_ushort(fd):
    return struct.unpack('<H', fd.read(2))[0]


def read_sbyte(fd):
    return struct.unpack('b', fd.read(1))[0]


def read_ubyte(fd):
    return struct.unpack('B', fd.read(1))[0]
