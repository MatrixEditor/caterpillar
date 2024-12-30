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

.. tab-set::

    .. tab-item:: Python

        >>> PLTEChunk = RGB[this.length / 3]

    .. tab-item:: Caterpillar C

        >>> PLTEChunk = RGB.__struct__[ContextPath("obj.length") / 3]

        .. versionadded:: 2.2.0
            The syntax will be changed once `__class_getitem__` is implemented by
            any :class:`.c.Struct` instance.

.. important::

    The length of the array is determined dynamically. In this case, the length is
    calculated by dividing the chunk's :code:`length` field by 3, since each :code:`RGB`
    object occupies 3 bytes.
