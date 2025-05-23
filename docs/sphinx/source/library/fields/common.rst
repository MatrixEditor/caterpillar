.. _fields-common:

**************
Common Structs
**************

Numeric Structs
---------------

.. autoclass:: caterpillar.py.PyStructFormattedField
    :members:

    .. versionchanged:: 2.4.0
        :code:`FormatField` renamed to :code:`PyStructFormattedField`

.. autoattribute:: caterpillar.py.uint8

.. autoattribute:: caterpillar.py.int8

.. autoattribute:: caterpillar.py.uint16

.. autoattribute:: caterpillar.py.int16

.. autoattribute:: caterpillar.py.uint32

.. autoattribute:: caterpillar.py.int32

.. autoattribute:: caterpillar.py.uint64

.. autoattribute:: caterpillar.py.int64

.. autoattribute:: caterpillar.py.size_t

.. autoattribute:: caterpillar.py.ssize_t

.. autoattribute:: caterpillar.py.float16

.. autoattribute:: caterpillar.py.float32

.. autoattribute:: caterpillar.py.float64

.. autoattribute:: caterpillar.py.void_ptr

.. autoattribute:: caterpillar.py.char

.. autoattribute:: caterpillar.py.boolean

.. autoattribute:: caterpillar.py.padding

.. autoclass:: caterpillar.py.Int
    :members:

.. autoclass:: caterpillar.py.UInt
    :members:

.. autoattribute:: caterpillar.py.vint

.. autoclass:: caterpillar.py.VarInt
    :members:

Bytes, Strings
--------------

.. autoclass:: caterpillar.py.Memory
    :members:

    .. versionchanged:: 2.4.0
        Removed :code:`encoding` argument

.. autoclass:: caterpillar.py.Bytes
    :members:

.. autoclass:: caterpillar.py.String
    :members:

.. autoclass:: caterpillar.py.Prefixed
    :members:

    .. versionadded:: 2.4.0
        Added support for arbitrary structs. **Warning: the second parameter is now a struct instead of the encoding string.**

.. autoclass:: caterpillar.py.CString
    :members:

.. autoclass:: caterpillar.py.ConstString
    :members:

.. autoclass:: caterpillar.py.ConstBytes
    :members:


Special Structs
---------------

.. autoattribute:: caterpillar.py.Pass

    See source code for details


.. autoclass:: caterpillar.py.Aligned
    :members:

    .. versionadded:: 2.4.0

.. autofunction:: caterpillar.py.align

    .. versionadded:: 2.4.0

.. autoclass:: caterpillar.py.Computed
    :members:

.. autoclass:: caterpillar.py.Transformer
    :members:

.. autoclass:: caterpillar.py.Enum
    :members:

.. autoclass:: caterpillar.py.Const
    :members:

.. autoclass:: caterpillar.py.Lazy
    :members:

.. autoclass:: caterpillar.py.Uuid
    :members:

    .. versionchanged:: 2.4.0
        :code:`uuid` renamed to :code:`Uuid`