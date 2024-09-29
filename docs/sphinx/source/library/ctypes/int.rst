.. _api-ctypes_int:

*************
Integer Types
*************

This document provides detailed API documentation for integer types in the :code:`caterpillar.c` module. These
integer types are low-level representations of integers with customizable bit-length, signedness, and byte
order. They are particularly useful when interacting with binary data or when a fixed-width integer
representation is required.

The integer types offered here are optimized for performance, making them more efficient than their Python
equivalents (:class:`FormatField`) in almost every context. The global predefined integer types (e.g.,
:data:`u8`, :data:`i32`) are convenient for most common cases, but you can also define custom integer types
with specific bit-widths, signedness, and endianness using the :class:`Int` class.

.. py:class:: caterpillar.c.Int(bits, signed=True, little_endian=True)

    This class implements an integer type with a variable number of bits,
    supporting signed and unsigned integers, and little-endian or big-endian
    byte orders.

    Unlike its Python counterpart (:class:`FormatField`), this C-based class
    focuses solely on integer operations, optimizing performance through direct
    use of the `int.from_bytes` and `int.to_bytes` methods. Although you can
    instantiate the class directly, it is recommended to use the global predefined
    instances for common integer types (see below for more details).

    .. note::
        For most use cases, utilize the pre-defined global instances like :data:`u8`,
        :data:`i16`, etc., for simplicity and efficiency.

    .. csv-table:: Supported Operations
        :header: "Action", "Operator", "Result"
        :widths: 15, 30, 30

        "Byteorder", ":code:`<endian> + <obj>`", "new :class:`Int` object with corresponding byteorder"
        "Sequence", ":code:`<obj>[<length>]`", ":class:`repeated` object"
        "Offset", ":code:`<obj> @ <offset>`", ":class:`atoffset` object"
        "Condition", ":code:`<obj> // <condition>`", ":class:`condition` object"
        "Switch", ":code:`<obj> >> <cases>`", ":class:`switch` object"

    .. versionadded:: 2.2.0


    .. py:method:: __init__(self, bits, signed=True, little_endian=True)

        Initializes the integer type with the given number of bits, sign specification,
        and byte order.

        :param int bits: The number of bits for the integer. Must be a multiple of 8.
        :param bool signed: Optional; whether the integer is signed. Defaults to True.
        :param bool little_endian: Optional; whether the integer should be stored in little-endian byte order. Defaults to True.

        .. code-block:: python
            :caption: Examples of using :class:`Int`

            from caterpillar.c import *

            # Unsigned 8-bit integer
            assert unpack(b"\x01", u8) == 1

            # Signed 8-bit integer
            assert pack(1, i8) == b"\x01"

            # Unsigned 16-bit little-endian integer
            assert unpack(b"\x01\x00", u16) == 1

            # Signed 16-bit big-endian integer
            assert pack(-1, Int(16, signed=True, little_endian=False)) == b"\xff\xff"

    .. py:method:: __repr__(self) -> str

        Returns a string representation of the integer type. The format of the returned string
        is as follows:

        .. code-block::

            <repr> := '<' ('le' | 'be') ['u'] 'int' <nbits> '>'

        >>> assert repr(u32) == "<le uint32>"

        :return: A string representation of the integer type, indicating the byte order, sign, and number of bits.

    .. py:method:: __type__(self) -> type

        Returns the Python type for this class. This is typically :code:`int`.

        :return: The Python type for this class.

    .. py:method:: __size__(self, ctx) -> int

        Returns the size in bytes of the integer type.

        >>> assert sizeof(u64) == 8

        :param ctx: The context object. (must not be null)
        :return: The size in bytes of the integer type.

    .. py:attribute:: nbytes
        :type: int

        The number of bytes in the integer, calculated from :attr:`nbits`.

    .. py:attribute:: nbits
        :type: int

        The number of bits in the integer.

        >>> assert u32.nbits == 32

    .. py:attribute:: signed
        :type: bool

        Indicates whether the integer is signed (True) or unsigned (False).

        >>> assert i8.signed is True

    .. py:attribute:: little_endian
        :type: bool

        Indicates whether the integer is stored in little-endian byte order (True) or big-endian byte order (False).

        >>> assert Int(32, little_endian=False).little_endian is False
        >>> assert (BIG_ENDIAN + u32).little_endian is False


Pre-Defined Integer Types (global)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. raw:: html

    <hr>

The following pre-defined integer types are globally available, optimized for
common use cases. By default, they use little-endian byte order. To switch to
big-endian, use the byteorder operation (e.g., :code:`BIG_ENDIAN + u16`).

Unsigned Integer Types:
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: caterpillar.c.u8

    Unsigned 8-bit integer type.

.. py:data:: caterpillar.c.u16

    Unsigned 16-bit integer type.

.. py:data:: caterpillar.c.u24

    Unsigned 24-bit integer type.

.. py:data:: caterpillar.c.u32

    Unsigned 32-bit integer type.

.. py:data:: caterpillar.c.u64

    Unsigned 64-bit integer type.

.. py:data:: caterpillar.c.u128

    Unsigned 128-bit integer type.


Signed Integer Types:
~~~~~~~~~~~~~~~~~~~~~

.. py:data:: caterpillar.c.i8

    Signed 8-bit integer type.

.. py:data:: caterpillar.c.i16

    Signed 16-bit integer type.

.. py:data:: caterpillar.c.i24

    Signed 24-bit integer type.

.. py:data:: caterpillar.c.i32

    Signed 32-bit integer type.

.. py:data:: caterpillar.c.i64

    Signed 64-bit integer type.

.. py:data:: caterpillar.c.i128

    Signed 128-bit integer type.
