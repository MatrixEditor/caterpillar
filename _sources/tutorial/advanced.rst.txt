.. _advanced-concepts:

*****************
Advanced Concepts
*****************

*TODO*

Now that you've acquired a general understanding of how this library works, let's
start the more advanced concepts. This document will bring the tutorial to a close,
leaving you well-equipped to create your own struct classes in Python.

.. attention::
    Most of the structs and techniques showcased here are subject to change, notably
    :class:`BitField`. Its current usage is not as user-friendly as someone might expect.


Operators
---------

Switch
^^^^^^

*TODO*

Offset
^^^^^^

*TODO*

BitFields
---------

*TODO* description

.. code-block:: python
    :caption: Implementing the `chunk-naming <https://www.w3.org/TR/png/#5Chunk-naming-conventions>`_ convention

    @bitfield(options={S_DISCARD_UNNAMED})
    class ChunkOptions:
        _            : 2        # <-- first two bits are not used
        ancillary    : 1        # f0
        _1           : 0
        _2           : 2
        private      : 1        # <-- the 5-th bit (from right to left)
        _3           : 0
        _4           : 2
        reserved     : 1        # f2
        _5           : 0        # <-- padding until the end of this byte
        _6           : 2
        safe_to_copy : 1        # f3

    # byte     :     0        1       2        3
    # bit      : 76543210 76543210 76543210 76543210
    # ----------------------------------------------
    # breakdown: 00100000 00100000 00100000 00100000
    #            \/|\___/ \/|\___/ \/|\___/ \/|\___/
    #            u f0 a   u f1 a   u f2  a  u f3 a
    # Where u='unnamed', a='added' and 'f..'=corresponding fields


Unions
------

This library introduces a special struct, namely *union*. What makes it special is
that **it behaves like a C-Union**. Really?


This library introduces a special struct, namely *union*. What makes it special is,
that **it behaves like a C-Union**. Really?

For example, let's combine the `chunk-naming <https://www.w3.org/TR/png/#5Chunk-naming-conventions>`_
convention with its bit options. You can use the bitfield from the previous section.

.. code-block:: python
    :caption: Combining the name with its naming convention

    @union
    class ChunkName:
        text: Bytes(4)
        options: ChunkOptions

Now, lets look at the bahaviour of an example object:

.. code-block:: python

    >>> obj = ChunkName()   # arguments optional
    >>> obj
    ChunkName(text=None, options=None)
    >>> obj.name = b"cHNk"  # lower-case 'k'
    >>> obj
    ChunkName(text=b'cHNk', options=ChunkOptions(..., safe_to_copy=True))
    >>> obj.name = b"cHNK"  # upper-case 'K'
    >>> obj
    ChunkName(text=b'cHNK', options=ChunkOptions(..., safe_to_copy=False))

As stated in the data model reference on :ref:`union-reference`, the constructor is the only
place, where the data does not get synchronized. In all other situations, the new value will
be applied to all other fields.

.. note::
    You can even write your own implementation of a :class:`UnionHook` to do whatever you
    want with the union object. Just specify the :code:`hook_cls` parameter in the union
    decorator.

The End!
--------

*TODO: implement final PNG struct*

