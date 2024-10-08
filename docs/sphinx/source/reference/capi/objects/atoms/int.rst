.. _reference-capi_intatom:

*************
Integer Atoms
*************

The :c:type:`CpIntAtomObject` is a specialized implementation for handling integers,
providing efficient mechanisms to pack and unpack sized integers. Unlike its Python
counterpart (:class:`FormatField`), this C-based class focuses solely on integer operations.


.. c:var:: PyTypeObject CpIntAtom_Type

    The type object for the :class:`~caterpillar.c.Int` class.

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


.. c:function:: int CpIntAtom_Pack(CpIntAtomObject* self, PyObject* value, CpLayerObject* layer)

    Packs the given value into the given layer. Returns ``-1`` if an error occurs.


.. c:function:: PyObject* CpIntAtom_Unpack(CpIntAtomObject* self, CpLayerObject* layer)

    Unpacks the value from the given layer. Returns *NULL* if an error occurs.


.. c:function:: int CpIntAtom_Check(PyObject *op)

    Checks if the given object is an :c:type:`CpIntAtomObject`


.. c:function:: int CpIntAtom_CheckExact(PyObject *op)

    Checks if the given object is an instance of an :c:type:`CpIntAtomObject`


.. rubric:: Runtime Performance

Measurements represent the accumulated runtime of one million calls to
:code:`unpack` or :code:`pack` using the corresponding implementation
in seconds.

.. list-table::
    :header-rows: 1
    :widths: 20 20 20 20 20

    * - Function
      - Caterpillar   [0]_
      - Caterpillar G [1]_
      - Caterpillar C [2]_
      - Construct     [3]_
    * - :code:`unpack`
      - 4.002179
      - 2.782663
      - 0.815902
      - 1.581962
    * - :code:`pack`
      - 3.866999
      - 2.707753
      - 0.926041
      - 1.587046


.. [0] local field instance
.. [1] global field instance
.. [2] C implementation
.. [3] Construct :code:`Int32sn`

The *benchmark* has been performed using the following code snippets:

.. code-block:: python
    :linenos:

    from caterpillar import _C, model, fields
    from construct import Int32sn

    # Caterpillar
    model.unpack(fields.Field(fields.int32), b"\x00\xFF\x00\xFF")

    # Caterpillar (Global)
    I32_G = fields.Field(fields.int32)
    model.unpack(I32_G, b"\x00\xFF\x00\xFF")

    # Caterpillar (C)
    _C.unpack(b"\x00\xFF\x00\xFF", _C.i32)

    # Construct
    Int32sn.parse(b"\x00\xFF\x00\xFF")
