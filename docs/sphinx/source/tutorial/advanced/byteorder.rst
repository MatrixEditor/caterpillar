.. _tutorial-dyn_byteorder:

Dynamic Byte Order
==================

In addition to traditional byte order types, *caterpillar* supports a dynamic byte order
based on the current pack or unpack context.

.. versionadded:: 2.6.4
    This feature is available in starting from version ``2.6.4``


There are various use-cases that require a struct to handle both big-endian and
little-endian. In order to reduce the amount of code for these structs, *caterpillar*
introduces a special byte order type: :class:`~caterpillar.byteorder.DynByteOrder`. It
supports two different configuration levels:

1. struct-wide: endianess is configured when calling :func:`~caterpillar.model.pack` or
   :func:`~caterpillar.model.unpack`.
2. field-level: byte order is applied per field

Each of these configuration levels support various methods of selecting the target endian:

* global configuration using an additional keyword argument in :func:`~caterpillar.model.pack` or
  :func:`~caterpillar.model.unpack`.
* context-key: configuration based on a value within the current context
* custom function: endian is derived from a custom function

Example: struct-wide dynamic byte order
---------------------------------------

Let's consider the following struct definition. The dynamic endian configuration will be applied
to all fields that haven't got an endian already set.

.. code-block:: python
    :linenos:

    @struct(order=Dynamic)
    class Format:
        a: uint16           # litte endian or big endian is decided using
        b: uint32           # a global context variable

    obj = Format(a=0x1234, b=0x56789ABC)

    # pack the object using BigEndian
    pack(obj, order=BigEndian)

    # now pack with little endian
    pack(obj, order=LittleEndian)

Here we pass an additional global context variable named :attr:`~caterpillar.context.CTX_ORDER` (``"_order"``)
to the packing and unpacking process. The dynamic endian will automatically infer the order based on this
global variable.

Example: field-level dynamic byte order
---------------------------------------

The same concept as shown above can be applied to single fields too. By default, the endian to use must be
given as a global context variable as described before.

.. code-block:: python
    :linenos:

    @struct(order=LittleEndian)
    class Format:
        a: uint16
        b: Dynamic + uint32   # only this field will be affected

    # packing and unpacking is the same as in the previous example


Example: context key reference
------------------------------

Sometimes format specifications use a special field indicating whether all following
fields are using big or little endian. To implement this kind of endian selection, a
so called *context key* can be specified, which can take one of the following forms:

*   direct reference: just a string reference

    .. code-block:: python

        # ...
        spec: uint8
        number: Dynamic(key="spec")
        # ...

*   context-lambda: a function that takes the current context as its first parameter and
    returns the target endian configuration value.

    .. code-block:: python

        # ...
        spec: uint8
        number: Dynamic(key=this.spec)
        # ...

The target endianess is decided based on the context value:

* :code:`str` will be applied directly as the format character
* any object storing a :code:`ch` string value
* any other object is converted to a :code:`bool` and the following mapping is applied:

  * :code:`True`: :attr:`~caterpillar.byteorder.LittleEndian`
  * :code:`False`: :attr:`~caterpillar.byteorder.BigEndian`

As an example, consider the following definition:

.. code-block:: python
    :linenos:

    @struct(order=BigEndian)
    class Format:
        spec: uint8 = 0
        a: DynByteOrder(key=this.spec) + uint16
        # alternatively
        # a: Dynamic(this.spec) + uint16
        b: uint32

    # packing and unpacking does not require the extra endian value
    obj = Format(spec=0, a=0x1234, b=0x56789ABC)
    # 0 -> False, results in BigEndian
    data_be = pack(obj)

    # 1 -> True, results in LittleEndian
    obj.spec = 1
    data_le = pack(obj)

