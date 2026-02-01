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

    Signed 16-bit integer field.

    Usage Example:
        >>> pack(1024, int16)
        b"\\x00\\x04"
        >>> unpack(int16, b"\\x00\\x04")
        1024

.. data:: caterpillar.fields.int16

    Unsigned 16-bit integer field.

    Usage Example:
        >>> pack(65535, uint16)
        b"\\xff\\xff"
        >>> unpack(uint16, b"\\xff\\xff")
        65535

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

.. data:: caterpillar.fields.size_t

    Unsigned platform-dependent size field. Size depends on the native architecture (32-bit or 64-bit).

    Usage Example:
        >>> pack(42, size)
        b"..."
        >>> unpack(size, b"...")
        42

    .. versionchanged:: 2.8.0
        renamed from ``size_t`` to `psize`

.. data:: caterpillar.fields.ssize_t

    Signed platform-dependent size field. Size depends on the native architecture (32-bit or 64-bit).

    Usage Example:
        >>> pack(42, ssize)
        b"..."
        >>> unpack(ssize, b"...")
        42

    .. versionchanged:: 2.8.0
        renamed from ``ssize_t`` to `pssize`

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

    Represents exactly one byte and maps it to a Python ``str`` of length 1.

    Usage Example:
        >>> pack("A", char)
        b"A"
        >>> unpack(char, b"A")
        'A'

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

    .. versionadded:: 2.4.0

.. autofunction:: caterpillar.fields.align

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