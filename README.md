RubyMarshal
===========

Read and write Ruby-marshalled data.

Installation
------------

    pip install rubymarshal

Usage
-----

  from rubymarshal.reader import loads, load
  from rubymarshal.writer import writes, write
  with open('my_file', 'rb') as fd:
      content = load(fd)
  with open('my_file', 'wb') as fd:
      write(fd, my_object)
  loads(b"\x04\bi\xfe\x00\xff")
  writes(-256)
  
Infos
-----

Code is on github: https://github.com/d9pouces/RubyMarshal.
Documentation is on readthedocs: 