# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'Matthieu Gallet'


class RubyClass(object):
    def __init__(self, cls, values):
        if isinstance(cls, Symbol):
            cls = cls.name
        self.cls = cls
        self.values = values

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.cls == other.cls and self.values == other.values

    def __hash__(self):
        return hash(hash(self.cls) + hash(self.values))

    def __repr__(self):
        return '%s:%s(%r)' % (self.__class__.__name__, self.cls, self.values)

    def __str__(self):
        return '%s:%s(%r)' % (self.__class__.__name__, self.cls, self.values)

    def __unicode__(self):
        return '%s:%s(%r)' % (self.__class__.__name__, self.cls, self.values)


class UsrMarshal(RubyClass):
    pass


class UserDef(RubyClass):
    pass


class Extended(RubyClass):
    pass


class Module(RubyClass):
    pass


class Object(RubyClass):
    def __init__(self, cls, values, **kwargs):
        self.kwargs = kwargs
        super(Object, self).__init__(cls, values)


class Symbol(object):

    __registered_symbols__ = {}

    def __new__(cls, name):
        if name in cls.__registered_symbols__:
            return cls.__registered_symbols__[name]
        return super(Symbol, cls).__new__(cls)

    def __init__(self, name):
        self.name = name
        self.__registered_symbols__[name] = self

    def __hash__(self):
        return hash('<<<:%s:>>>' % self.name)

    def __repr__(self):
        return 'Symbol("%s")' % self.name

    def __str__(self):
        return ':%s' % self.name

    def __unicode__(self):
        return ':%s' % self.name
