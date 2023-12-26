Welcome to Caterpillar's documentation!
=======================================

*caterpillar* is a powerful python framework designed to navigate through structured
binary data. This framework operates as a declarative parser and builder using standard
Python class definitions and annotations.

.. caution::
   Before using this library, be aware that the current status is "beta/testing". Therefore,
   expect bugs and undocumented issues. Additionally, the documentation is a WIP.


Whetting Your Appetite
----------------------

If you're involved in reverse engineering or working with custom or proprietary file
formats, there often comes a need to structure data in a way that is both easy and
efficient.

🐛 lets you define standard structs with a fixed size while also supporting dynamic
structs that adjust their size based on the current context. This framework enables you
to write complex structures in a compact and readable manner.

.. code-block::
   :caption: Simple example of a custom struct

   @struct
   class Format:
      magic: b"Foo"                       # constant values
      name: CString(...)                  # C-String without a fixed length
      value: le + uint16                  # little endian encoding
      entries: be + CString[uint32::]     # arrays with big-endian prefixed length

.. admonition:: Hold up, wait a minute!

   How does this even work? Is this still Python? Answers to these questions and more are given
   in the general :ref:`introduction`.

Working with defined classes is as straightforward as working with normal classes. *All
constant values are created automatically!*

>>> obj = Format(name="Hello, World!", value=10, entries=["Bar", "Baz"])
>>> print(obj)
Format(magic=b'Foo', name='Hello, World!', value=10, entries=['Bar', 'Baz'])

Packing and unpacking have never been easier:

>>> pack(obj)
b'FooHello, World!\x00\n\x00\x00\x00\x00\x02Bar\x00Baz\x00'
>>> unpack(Format, _)
Format(magic=b'Foo', name='Hello, World!', value=10, entries=['Bar', 'Baz'])

.. admonition:: What about documentation?

   There are specialized options created only for documentation purposes, so you don't
   have to worry about documenting fields. Just apply the documentation as usual.


Where to start?
---------------

It is recommended to take a look at the explanation of the internal :ref:`datamodel` to get
in touch with all forms of structs. Additionally, there's a detailed documentation on
what configuration options can be used. Alternatively you can follow the :ref:`tutorial-index`.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents:

   installing/index.rst
   tutorial/index.rst
   reference/index.rst
   library/index.rst
   development/index.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
