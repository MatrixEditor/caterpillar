.. _turotial-basics:

**************
Basic Concepts
**************

In this section, we will introduce some fundamental techniques commonly used when working
with binary file formats. These concepts lay the foundation for understanding more advanced
topics covered in the next chapter.

.. note::

    **Applies for** :code:`caterpillar<2.6.0`.

    To simplify field definitions in your structs, we can use shortcuts. For instance, instead
    of manually specifying field types, we can leverage the :code:`F` function from the
    :code:`caterpillar.shortcuts` module to create fields. However, if your don't want to
    wrap everything within a :class:`~caterpillar.py.Field`, you can use the :code:`as_field`
    option when packing or unpacking.

    >>> from caterpillar.shortcuts import F
    >>> field = F(uint8)

    or wrap the struct directly

    >>> pack(0xFF, uint8, as_field=True)




.. toctree::
    :maxdepth: 2
    :caption: Basic Concepts

    stdtypes
    string
    bytes
    padding
    context
    other