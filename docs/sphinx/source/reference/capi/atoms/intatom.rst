.. _reference-capi_intatom:

*************
Integer Atoms
*************

The :c:type:`CpIntAtomObject` is a specialized implementation for handling integers,
providing efficient mechanisms to pack and unpack sized integers. Unlike its Python
counterpart (:class:`FormatField`), this C-based class focuses solely on integer operations.


.. c:var:: PyTypeObject CpIntAtom_Type

    The type object for the :c:type:`intatom` class.

This implementation utilizes :code:`int.from_bytes` and :code:`int.to_bytes`. Direct C
calls are optimized, reducing runtime overhead compared to Python.

.. c:type:: CpIntAtomObject

    A fundamental class for managing fixed-size integers. Further recommendations for optimal
    use are detailed below.

    .. c:var:: PyObject * m_byte_count

        Represents the number of bytes in the integer. This can be accessed in Python using the attribute :code:`nbytes`.

    .. c:var:: int _m_signed

        Indicates whether the integer is signed. A value of ``1`` means signed, and ``0`` means unsigned.

    .. c:var:: int _m_little_endian

        Indicates the endianness of the integer. A value of ``1`` signifies little-endian, while ``0`` signifies big-endian.


Recommendations
---------------

The following examples illustrate how to effectively utilize the :c:type:`intatom` class
and the associated methods:

.. code-block:: python
    :linenos:

    from caterpillar._C import LITTLE_ENDIAN as le
    from caterpillar._C import intatom, unpack, i16

    # Define a global 16-bit little-endian signed integer atom
    I16_LE = le + i16
    _I16_LE = intatom(16, signed=True, little_endian=True)

    unpack(b"\x01\x02", _I16_LE)
    unpack(b"\x01\x02", intatom(16, signed=True, little_endian=True))
    unpack(b"\x01\x02", I16_LE)
    unpack(b"\x01\x02", le + i16)

*TODO: describe the impact on runtime overhead of these four methods*

