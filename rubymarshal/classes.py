__author__ = "Matthieu Gallet"


class RubyClass:
    def __init__(self, cls, values):
        # if isinstance(cls, Symbol):
        #     cls = cls.name
        self.cls = cls
        self.values = values

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.cls == other.cls
            and self.values == other.values
        )

    def __hash__(self):
        return hash(hash(self.cls) + hash(repr(self.values)))

    def __repr__(self):
        return "%s:%s(%r)" % (self.__class__.__name__, self.cls, self.values)

    def __str__(self):
        return "%s:%s(%r)" % (self.__class__.__name__, self.cls, self.values)


class String:
    def __init__(self, text: str, attrs=None):
        self.value = str(text)
        self.attrs = attrs or {}

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, String):
            return self.value == other.value and self.attrs == other.attrs
        return False

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return self.value

    def __add__(self, other):
        return String(self.value + str(other), self.attrs)

    def __ne__(self, other):
        if isinstance(other, str):
            return self.value != other
        elif isinstance(other, String):
            return self.value != other.value or self.attrs != other.attrs
        return False

    def __lt__(self, other):
        return self.value < other

    def __gt__(self, other):
        return self.value > other

    def __le__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __iter__(self):
        yield from self.value

    def __bool__(self):
        return bool(self.value)

    def __getitem__(self, item):
        return self.value[item]

    def __len__(self):
        return len(self.value)

    def encode(self, *args, **kwargs):
        return self.value.encode(*args, **kwargs)


class Class(RubyClass):
    pass


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


class Symbol:

    __registered_symbols__ = {}

    def __new__(cls, name):
        if name in cls.__registered_symbols__:
            return cls.__registered_symbols__[name]
        return super(Symbol, cls).__new__(cls)

    def __init__(self, name):
        self.name = name
        self.__registered_symbols__[name] = self

    def __hash__(self):
        return hash("<<<:%s:>>>" % self.name)

    def __repr__(self):
        return 'Symbol("%s")' % self.name

    def __str__(self):
        return ":%s" % self.name

    def encode(self, *args, **kwargs):
        return self.name.encode(*args, **kwargs)
