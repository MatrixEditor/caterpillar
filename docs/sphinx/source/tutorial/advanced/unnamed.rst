.. _tutorial-unnamed:

Unnamed
=======

The previous section introduced :ref:`tutorial-union`, which mimics a C union at the level
of a whole struct: every field of the struct shares the same memory, and assigning one field
updates all the others. :class:`~caterpillar.fields.Unnamed` brings the same idea down to a
single *field*: one position in a struct that may hold any one of several possible types, all
read from - and written to - the very same window of bytes.

Where a *union* struct eagerly keeps every field in sync, an :class:`~caterpillar.fields.Unnamed`
field is lazy: the fixed-size bytes are read once, immediately, like any other field, but no
particular interpretation of those bytes is decoded until you actually ask for it.

A basic example
----------------

Suppose a record stores a 4-byte value that should sometimes be read as a 32-bit integer, and
sometimes as a short ASCII tag. Instead of declaring two separate fields and manually keeping
track of which one is meaningful, declare a single :code:`Unnamed[...]` field listing both
possible types:

.. code-block:: python
    :caption: A field that can be read as either an integer or a tag

    @struct
    class Record:
        kind: uint16
        value: Unnamed[uint32, CString(4)]

Unpacking reads the 2-byte :code:`kind` field plus exactly 4 bytes for :code:`value` - the
size of the largest member - up front. Neither :code:`uint32` nor :code:`CString` is decoded
yet at this point:

>>> obj = unpack(Record, b"\x01\x00ABCD")
>>> obj.value[0]          # decode as uint32, then cache it
1145258561
>>> obj.value._1          # decode as CString, then cache it
'ABCD'
>>> obj.value
Unnamed(1145258561, 'ABCD')

Both :code:`value[i]` (works with any integer, including negative indices) and the shorthand
attribute form :code:`value._i` are equivalent.

Sizing
------

By default, the field is sized as the *largest* member (so every member must have a fixed,
statically-known size). Use :code:`.sized(...)` to declare an explicit size instead - a plain
:code:`int`, or a context lambda evaluated against the enclosing struct, exactly like sizing a
sequence:

.. code-block:: python
    :caption: Explicit, context-dependent sizing

    @struct
    class Record:
        length: uint16
        value: Unnamed[uint32, uint16].sized(this.length)
        # using sized[...] expression is also possible (must be last item)
        .. value: Unnamed[uint32, uint16, sized[this.length]]

Building a value for packing
------------------------------

An :class:`~caterpillar.fields.Unnamed` value does not have to come from :code:`unpack(...)` -
you can construct one directly to pack it. All of the following are valid:

>>> Unnamed()                  # nothing assigned yet - cannot be packed like this
Unnamed()
>>> Unnamed(1, 2, 3)           # positional arguments fill index 0, 1, 2, ...
Unnamed(1, 2, 3)
>>> Unnamed(_1="XY")           # keyword arguments (``_<index>``) set one index directly
Unnamed(?, 'XY')

Since a positional-then-keyword call is processed left to right, whichever index was assigned
*last* is the one that ends up encoded when the value is packed.

>>> pack(Record(kind=1, value=Unnamed(_1="XY")))
b'\x01\x00XY\x00\x00'
>>> pack(Record(kind=2, value=Unnamed(0xCAFEBABE)))
b'\x02\x00\xbe\xba\xfe\xca'


