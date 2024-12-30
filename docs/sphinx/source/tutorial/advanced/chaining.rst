.. _tutorial-chaining:

Chaining
========

It is also possible to create a chain of structs, where one struct's
output becomes the input for another. This allows for flexible data
processing pipelines, where you can perform multiple operations on
the data sequentially. However, this feature is generally not recommended
for most use cases, as it can introduce complexity and impact performance
in some scenarios.

How it works
------------

When you chain structs together, the resulting data is processed in a
pipeline fashion: unpacking flows from head to tail, while packing moves
from tail to head. This means that when unpacking, each struct in the
chain processes the data in the order specified, and when packing,
the order is reversed.

For example, consider the following code that chains two operations:

>>> chain = ZLibCompressed(...) & Format

In this example, the :code:`ZLibCompressed` struct is applied first to decompress
the data, and once decompression is complete, the :code:`Format.__unpack__` method
is called to further process the data.

.. note::
  It is important to note that a chained struct is **not** treated as a field.
  Instead, it is a combined structure where each part of the chain operates on
  the data sequentially. (see :class:`~caterpillar.py.Chain`)