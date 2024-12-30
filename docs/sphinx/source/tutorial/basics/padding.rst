.. _tutorial-basics_padding:

*******
Padding
*******

.. attention::
    This section is subject to change if :code:`Padding` is implemented.


In binary file formats, padding is often used to align data to certain byte
boundaries. *Caterpillar* provides a way to handle padding within structs.
However, it is important to note that *caterpillar* doesn't store any data
associated with the padding itself unless explicitly defined. If you need
to retain or manipulate the padding content, you can use the :code:`Bytes` or
:code:`Memory` field types.

If you want to apply padding to a struct, you can simply specify the padding
length using the `padding` keyword. This is useful when you need to ensure
that certain fields are aligned or when the structure requires reserved spaces.

>>> field = padding[10] # greedy or dynamic size
