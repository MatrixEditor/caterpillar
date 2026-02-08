.. _first_steps-inline-syntax:

Inline Syntax
=============

In addition to the standard methods for packing and unpacking data, *Caterpillar* also
supports an **inline syntax** feature that allows for more concise and expressive data
parsing. This syntax uses Python's overloaded left-shift operator (``<<``) to easily
unpack data from a bytes object or a stream, making the code both compact and readable.

Unpacking Data Inline
^^^^^^^^^^^^^^^^^^^^^^

With the inline syntax, you can unpack binary data into a struct directly using the
left-shift operator. This operator is a shorthand for calling the ``from_bytes`` method,
which means you don't need to explicitly invoke a function to parse your data.

.. code-block:: python

    from io import BytesIO
    from caterpillar.py import uint8

    # data can be unpacked INLINE using a special operator
    data = b"\x00\x00\x01\xff"

    # If using on a static bytes object, the struct will always begin at offset zero
    value1 = uint8 << data
    value2 = uint8 << data
    assert value1 == value2


In the example above, the binary data is unpacked into the :data:`~caterpillar.fields.uint8` struct.
The left-shift operator (``<<``) reads the data starting at the beginning of the byte stream and
automatically handles the parsing for you.

When using a stream, the operator will start unpacking from the current position in the stream. This
is useful for processing data incrementally or when you want to track your stream's current position
manually.

>>> stream = BytesIO(data)
>>> stream.seek(2)  # Move the stream position to byte index 2
>>> uint8 << stream
1

Wrapper methods
^^^^^^^^^^^^^^^

Instead of using the special operator, all struct classes in *Caterpillar* also provide the typical
wrapper functions for packing and unpacking:

>>> # Instead of using the special operator, all default struct classes provide
>>> # wrapper functions for packing and unpacking:
>>> uint8.from_bytes(data)
0
>>> uint8.to_bytes(0xFF)
b"\0xFF"

This inline syntax feature is great for simplifying your code when dealing with binary data, making the
code both more readable and intuitive.
