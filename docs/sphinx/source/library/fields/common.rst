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

.. autoattribute:: caterpillar.fields.uint8
.. autoattribute:: caterpillar.fields.int8
.. autoattribute:: caterpillar.fields.uint16
.. autoattribute:: caterpillar.fields.int16
.. autoattribute:: caterpillar.fields.uint32
.. autoattribute:: caterpillar.fields.int32
.. autoattribute:: caterpillar.fields.uint64
.. autoattribute:: caterpillar.fields.int64
.. autoattribute:: caterpillar.fields.size_t
.. autoattribute:: caterpillar.fields.ssize_t
.. autoattribute:: caterpillar.fields.float16
.. autoattribute:: caterpillar.fields.float32
.. autoattribute:: caterpillar.fields.float64
.. autoattribute:: caterpillar.fields.void_ptr
.. autoattribute:: caterpillar.fields.char
.. autoattribute:: caterpillar.fields.boolean
.. autoattribute:: caterpillar.fields.padding

.. autoclass:: caterpillar.fields.Int
    :members:

.. autoclass:: caterpillar.fields.UInt
    :members:

.. autoattribute:: caterpillar.fields.vint

.. autoclass:: caterpillar.fields.VarInt
    :members:

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

.. autoattribute:: caterpillar.fields.Pass

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

.. autoclass:: caterpillar.fields.Uuid
    :members:

    .. versionchanged:: 2.4.0
        :code:`uuid` renamed to :code:`Uuid`