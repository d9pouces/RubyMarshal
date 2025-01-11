"""Mutations for RubyMarshal."""
import pytest_mutagen as mg

from rubymarshal.classes import RubyObject, RubyString
from rubymarshal.reader import Reader
from rubymarshal.writer import Writer

# classes.py

function_list = ["__hash__", "__repr__", "__str__"]
mg.trivial_mutations(function_list, RubyObject)

function_list = [
    "__ne__",
    "__add__",
    "__hash__",
    "__repr__",
    "__str__",
    "__lt__",
    "__gt__",
    "__le__",
    "__ge__",
    "__iter__",
    "__bool__",
    "__getitem__",
    "__len__",
]
mg.trivial_mutations(function_list, RubyString)

# utils.py

# Nothing interesting found """

# writer.py


function_list = ["write_python_object"]
mg.trivial_mutations(function_list, Writer)

# reader.py


mg.trivial_mutations("read_symbol", Reader)
