.. _offset-tutorial:

Offsets
=======

Offsets introduce a unique challenge in binary packing, as we often need to ensure
that new data is written to the correct location in the stream without accidentally
overwriting any previously written data. *Caterpillar* automatically solves this
problem for you, simplifying the management of offsets when working with structs and
fields.

An offset in the context of binary packing refers to a specified location within the
binary data stream where the next piece of data should be written. This is often needed
when you're working with binary file formats or communication protocols that require
data to be placed at specific byte positions.

For example, when packing data into a binary stream, you might need to ensure that certain
fields or data structures start at specific offsets. This is common in binary file formats,
where fields must appear at certain byte positions in the file.

*In general, offsets are used to control where data is placed relative to other data
that has already been packed.*

In *caterpillar*, you can apply offsets to fields or structs using the :code:`@` operator, but
it's important to understand the following guidelines:

1. **Fields**: You can directly apply offsets to individual fields of a struct.
2. **Structs**: You cannot directly apply offsets to custom-defined struct classes. These need to be wrapped using the :class:`Field` class.

Here's an example to clarify the concept:

.. code-block:: python

    >>> field = uint32 @ 0x1234     # ok
    >>> struct = Format @ 0x1234    # not okay
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
    TypeError: unsupported operand type(s) for @: 'type' and 'int'
    >>> field = Field(Format) @ 0x1234  # ok

*TODO* explain internal mechanism of storing an offset map