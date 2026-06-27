.. _fields-common:

**************
Common Structs
**************

Numeric Structs
---------------

.. autoclass:: caterpillar.fields.PyStructFormattedField
    :members:

    .. versionchanged:: 2.4.0
        :code:`FormatField` renamed to :code:`PyStructFormattedField`

    .. versionchanged:: 2.8.1
        Dropped support for format character ``'x'``. Use the :class:`Padding` type instead.

Formatted fields use Python's :mod:`struct` module internally. Static single
values and arrays require exact reads during unpacking; short streams raise
:class:`~caterpillar.exception.ValidationError`.

.. data:: caterpillar.fields.uint8

    Unsigned 8-bit integer field. Range: ``0`` to ``255``.

    Usage Example:
        >>> pack(250, uint8)
        b"\\xfa"
        >>> unpack(uint8, b"\\xfa")
        250

.. data:: caterpillar.fields.int8

    Signed 8-bit integer field. Range: ``-128`` to ``127``.

    Usage Example:
        >>> pack(-5, int8)
        b"\\xfb"
        >>> unpack(int8, b"\\xfb")
        -5

.. data:: caterpillar.fields.uint16

    Unsigned 16-bit integer field. Range: ``0`` to ``65535``.

    Usage Example:
        >>> pack(65535, uint16)
        b"\\xff\\xff"
        >>> unpack(uint16, b"\\xff\\xff")
        65535

.. data:: caterpillar.fields.int16

    Signed 16-bit integer field. Range: ``-32768`` to ``32767``.

    Usage Example:
        >>> pack(1024, int16)
        b"\\x00\\x04"
        >>> unpack(int16, b"\\x00\\x04")
        1024

.. data:: caterpillar.fields.uint24

    Unsigned 24-bit integer field implemented by :class:`UInt`.

.. data:: caterpillar.fields.int24

    Signed 24-bit integer field implemented by :class:`Int`.

.. data:: caterpillar.fields.uint32

    Unsigned 32-bit integer field.

    Usage Example:
        >>> pack(123456, uint32)
        b"@\\xe2\\x01\\x00"
        >>> unpack(uint32, b"@\\xe2\\x01\\x00")
        123456

.. data:: caterpillar.fields.int32

    Signed 32-bit integer field.

    Usage Example:
        >>> pack(123456, int32)
        b"@\\xe2\\x01\\x00"
        >>> unpack(int32, b"@\\xe2\\x01\\x00")
        123456

.. data:: caterpillar.fields.uint64

    Unsigned 64-bit integer field.

    Usage Example:
        >>> pack(1, uint64)
        b"\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00"
        >>> unpack(uint64, b"\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00")
        1

.. data:: caterpillar.fields.int64

    Signed 64-bit integer field.

    Usage Example:
        >>> pack(-1, int64)
        b"\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff"
        >>> unpack(int64, b"\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff")
        -1

.. data:: caterpillar.fields.psize

    Unsigned platform-dependent size field. Size depends on the native architecture (32-bit or 64-bit).
    The typing alias is available as :data:`caterpillar.types.size_t`.

.. data:: caterpillar.fields.pssize

    Signed platform-dependent size field. Size depends on the native architecture (32-bit or 64-bit).
    The typing alias is available as :data:`caterpillar.types.ssize_t`.

    .. versionchanged:: 2.8.0
        The field instances were renamed from ``size_t`` / ``ssize_t`` to
        ``psize`` / ``pssize`` to avoid colliding with the typing aliases.

.. data:: caterpillar.fields.float16

    Half-precision (16-bit) floating point field.

    Usage Example:
        >>> pack(1.5, float16)
        b"..."
        >>> unpack(float16, b"...")
        1.5

.. data:: caterpillar.fields.float32

    Single-precision (32-bit) floating point field.

    Usage Example:
        >>> pack(3.14, float32)
        b"..."
        >>> unpack(float32, b"...")
        3.14

.. data:: caterpillar.fields.float64

    Double-precision (64-bit) floating point field.

    Usage Example:
        >>> pack(3.14, float64)
        b"..."
        >>> unpack(float64, b"...")
        3.14

.. data:: caterpillar.fields.void_ptr

    Void pointer field represented as an integer memory address.

    Usage Example:
        >>> pack(0x1000, void_ptr)
        b"..."
        >>> unpack(void_ptr, b"...")
        4096

.. data:: caterpillar.fields.char

    Represents exactly one byte using Python's ``struct`` ``"c"`` format.
    Values packed with this field must be one-byte ``bytes`` objects.

    Usage Example:
        >>> pack(b"A", char)
        b"A"
        >>> unpack(char, b"A")
        b'A'

.. data:: caterpillar.fields.boolean

    Boolean field stored as a single byte. Encoded as ``0x00`` for ``False`` and ``0x01`` for ``True``.

    Usage Example:
        >>> pack(True, boolean)
        b"\\x01"
        >>> unpack(boolean, b"\\x00")
        False


.. autoclass:: caterpillar.fields.Int
    :members:

.. autoclass:: caterpillar.fields.UInt
    :members:

.. autoattribute:: caterpillar.fields.vint

.. autoclass:: caterpillar.fields.VarInt
    :members:

Pointers
~~~~~~~~

.. autoclass:: caterpillar.fields.pointer
    :members:

.. autoclass:: caterpillar.fields.Pointer
    :members:

.. autoclass:: caterpillar.fields.relative_pointer
    :members:

.. autoclass:: caterpillar.fields.RelativePointer
    :members:

.. autofunction:: caterpillar.fields.uintptr_fn
.. autofunction:: caterpillar.fields.intptr_fn

Bytes, Strings
--------------

Fixed-size :class:`Memory`, :class:`Bytes`, :class:`String`, and
:class:`CString` instances read exactly the configured byte length. If the
stream ends early, unpacking raises
:class:`~caterpillar.exception.ValidationError`. Greedy forms continue to read
until EOF or, for :class:`CString`, until the padding byte is encountered.

.. autoclass:: caterpillar.fields.Memory
    :members:

    .. versionchanged:: 2.4.0
        Removed :code:`encoding` argument

.. autoclass:: caterpillar.fields.Bytes
    :members:

.. autoclass:: caterpillar.fields.String
    :members:

.. autoclass:: caterpillar.fields.Prefixed
    :members:

    .. versionadded:: 2.4.0
        Added support for arbitrary structs. **Warning: the second parameter is now a struct instead of the encoding string.**

.. autoclass:: caterpillar.fields.CString
    :members:

    Fixed-length C strings are measured in encoded bytes, not Python
    characters. During packing, the encoded byte sequence must fit in the
    configured length and is padded with the configured single-byte padding
    value. During unpacking, exactly that many bytes are read and trailing
    padding bytes are stripped before decoding.

    .. code-block:: python

        >>> pack("ä", CString(2, encoding="utf-8"), as_field=True)
        b'\\xc3\\xa4'
        >>> pack("ä", CString(1, encoding="utf-8"), as_field=True)
        Traceback (most recent call last):
        ...
        ValidationError: String 'ä' is too long for the fixed length of 1 bytes. Got 2 bytes.

.. autoclass:: caterpillar.fields.ConstString
    :members:

.. autoclass:: caterpillar.fields.ConstBytes
    :members:


Special Structs
---------------

.. data:: caterpillar.fields.padding

    Default instance of :class:`Padding` that uses a null-byte as the fill pattern.

.. autoclass:: caterpillar.fields.Padding
    :members:

    .. versionchanged:: 2.8.0
        Added support for customizable padding objects.

.. autodata:: caterpillar.fields.Pass

    See source code for details


.. autoclass:: caterpillar.fields.Aligned
    :members:

    ``alignment`` is expressed in bytes and must resolve to a positive power of
    two. Padding is calculated from the current stream position, so an already
    aligned position adds zero bytes.

    .. versionadded:: 2.4.0

.. autofunction:: caterpillar.fields.align

    Returns a context lambda that computes the padding needed to reach the next
    multiple of ``alignment`` from the current stream position. ``alignment``
    follows the same positive-power-of-two rule as :class:`Aligned`.

    .. versionadded:: 2.4.0

.. autoclass:: caterpillar.fields.Computed
    :members:

.. autoclass:: caterpillar.fields.Transformer
    :members:

    .. versionchanged:: 2.5.0
        Removed ``__fmt__`` method

.. autoclass:: caterpillar.fields.Enum
    :members:

.. autoclass:: caterpillar.fields.Const
    :members:

.. autoclass:: caterpillar.fields.Lazy
    :members:

.. autodata:: caterpillar.fields.Uuid

    .. versionchanged:: 2.4.0
        :code:`uuid` renamed to :code:`Uuid`

.. autoclass:: caterpillar.fields.AsLengthRef
    :members:
    :private-members:

    .. versionadded:: 2.6.0

.. autoclass:: caterpillar.fields.Timestamp
    :members:
    :private-members:

    .. versionadded:: 2.8.0