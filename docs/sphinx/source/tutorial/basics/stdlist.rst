.. _tutorial-basics-stdtypes_list:

**************
Arrays / Lists
**************

When working with binary formats, it's common to store multiple objects of the
same type in a sequence, such as a list or array. *Caterpillar* simplifies this
task by allowing easy access to items and defining arrays with both static and
dynamic sizes.

For example, let's consider the `PLTE <https://www.w3.org/TR/png/#11PLTE>`_ chunk
from the PNG format, which stores a sequence of three-byte RGB objects. To define
an array of RGB objects, you can use the following syntax:

>>> PLTEChunk = RGB[this.length / 3]

.. tip::
    If you want to remove the typing issues associated with the getitem (``[]``)
    operation, add these lines to the ``RGB`` class definition:

    .. code-block:: python

        @struct
        class RGB:
            # ... previous code ...
            if typing.TYPE_CHECKING:
                def __class_getitem__(cls, length): ...

To use the faster :class:`Repeated` class provided by the C-extension:

>>> from caterpillar.c import Repeated
>>> from caterpillar.shared import getstruct
>>> PLTEChunk = Repeated(getstruct(RGB), this.length / 3)


.. important::

    The length of the array is determined dynamically. In this case, the length is
    calculated by dividing the chunk's :code:`length` field by 3, since each :code:`RGB`
    object occupies 3 bytes.

