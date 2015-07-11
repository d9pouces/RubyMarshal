.. RubyMarshal documentation master file, created by
   sphinx-quickstart on Wed Feb 13 11:51:12 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RubyMarshal's documentation
===========================

overview
--------

Read and write Ruby-marshalled data.
Only basics Ruby data types can be read and written:

  * `float`,
  * `bool`,
  * `int`,
  * `str` (mapped to `unicode` in Python 2),
  * `nil` (mapped to `None` in Python),
  * `array` (mapped to `list`),
  * `hash` (mapped to `dict`),
  * symbols and other classes are mapped to specific Python classes.

.. code-block:: python

  from rubymarshal.reader import loads, load
  from rubymarshal.writer import writes, write
  with open('my_file', 'rb') as fd:
      content = load(fd)
  with open('my_file', 'wb') as fd:
      write(fd, my_object)
  loads(b"\x04\bi\xfe\x00\xff")
  writes(-256)

installation
------------

.. code-block:: bash

    pip install rubymarshal


:doc:`api/index`
    The complete API documentation, organized by modules


Full table of contents
======================

.. toctree::
   :maxdepth: 4

   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
