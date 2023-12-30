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

By now, you should already know that there are special :ref:`operators` that can be used
with structs, for example :code:`[]` for array creation or :code:`+` to apply an endianess
configuration.

.. _switch-tutorial:

Switch
^^^^^^

*caterpillar* comes with native support for switch-case structures. There is no need for
a custom implementation that would unnecessarily slow down the packing or unpacking
process.

Although there are limitations to :ref:`operators`, its basic behavior should be
more than enough to work with. Let's go back to our PNG implementation and finally define
the common chunk type:

.. code-block:: python
    :caption: Implementation of the general `chunk layout <https://www.w3.org/TR/png/#5Chunk-layout>`_

    @struct(order=BigEndian)
    class PNGChunk:
        length: uint32          # length of the data field
        type: Bytes(4)
        data: F(this.type) >> { # just use right shift
            b"IHDR": IHDRChunk,
            b"PLTE": PLTEChunk, # the key must be comparable to this.type
            b"pHYs": PHYSChunk,
            b"iTXt": ITXTChunk,
            b"tIME": TIMEChunk,
            b"tEXt": TEXTChunk,
            b"iTXt": ITXTChunk,
            b"fDAT": FDATChunk,
            b"zTXt": ZTXTChunk,
            b"gAMA": GAMAChunk,
            # Special chunk: we don't need to parse any data
            b"IEND": Pass
            # As we don't define all chunks here for now, a default
            # option must be provided
            DEFAULT_OPTION: Memory(this.length)
        }


Offset
^^^^^^

Offsets introduce a special challenge to binary packing as we don't want to override data
that was previously written to the stream. This library will solve that problem for you
automatically!

In general, you can use the :code:`@` operator with structs and fields, but not custom defined class
structs. They have to be wrapped by a :class:`Field` first:

.. code-block:: python

    >>> field = uint32 @ 0x1234     # ok
    >>> struct = Format @ 0x1234    # not okay
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
    TypeError: unsupported operand type(s) for @: 'type' and 'int'
    >>> field = F(Format) @ 0x1234  # ok


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

We finish this tutorial by completing our PNG format implementation. As the format is just
a collection of chunks, we can simply alter the *main* struct from before:

.. code-block:: python
    :caption: Final PNG implementation

    @struct
    class PNG:
        magic: b"\x89PNG\x0D\x0A\x1A\x0A"
        # We don't know the length, therefore we need greedy parsing
        chunks: PNGChunk[...]

**Thats it!** We now have a qualified PNG image parser **and** builder just using some
Python class definitions.

.. code-block:: python
    :caption: Sample usage of the PNG struct

    >>> image = unpack_file(PNG, "/path/to/image.png")
    >>> image
    PNG(magic=b'\x89PNG\r\n\x1a\n', chunks=[PNGChunk(length=13,type='IHDR', body=..., crc=258163462), ...])
    >>> pack_file(image, "/path/to/destination")


*This is the end of our journy to the basics of caterpillar. Below is a collection of useful
resources that might help you progress any further.*

.. seealso::
    * :ref:`reference-index`
    * :ref:`library-index` API Docs
    * `Github Source <https://github.com/MatrixEditor/caterpillar>`_
    * `Implemented Formats <https://github.com/MatrixEditor/caterpillar/tree/master/examples/formats>`_

