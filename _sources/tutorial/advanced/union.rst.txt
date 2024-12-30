.. _tutorial-union:

Unions
======

A **Union** is a special type of structure that mimics the behavior of a C-style union. In a C
union, multiple fields share the same memory space, meaning only one field can store a value
at any given time. The value of the most recently assigned field overwrites the previous one.
*Caterpillar* brings this concept to Python, allowing you to define structs where multiple
fields share the same underlying storage, and the value of one field automatically reflects
in others when it changes.

A union is defined using the :code:`@union` decorator. Fields in the union share memory, meaning when
you assign a value to one field, the value is automatically synchronized with other fields that
are part of the union. The generated struct will always use the size of the largest field.

To demonstrate this, let's combine the **chunk-naming convention** (as used in PNG file
formats, see :ref:`tutorial-bitfield`) with its associated bit options from the previous
section. We can define a union where the chunk name is a string and the options are packed
in a bitfield.

.. code-block:: python
    :caption: Combining the name with its naming convention

    @union
    class ChunkName:
        text: Bytes(4)
        options: ChunkOptions

When you assign a value to one of the fields in the union, the other fields will automatically
reflect that change. This synchronization happens **after the initial constructor**; any
modification made to one field automatically updates the corresponding field.

Here's an example demonstrating the behavior of the :code:`ChunkName` union:

>>> obj = ChunkName()   # arguments optional
>>> obj
ChunkName(text=None, options=None)
>>> obj.name = b"cHNk"  # lower-case 'k'
>>> obj
ChunkName(text=b'cHNk', options=ChunkOptions(..., safe_to_copy=True))
>>> obj.name = b"cHNK"  # upper-case 'K'
>>> obj
ChunkName(text=b'cHNK', options=ChunkOptions(..., safe_to_copy=False))

How this can work
-----------------

When a union object is first created, the fields do not synchronize immediately.
You can set values for fields independently during the construction of the object.
After the object is constructed, any change to one of the union's fields automatically
updates the other fields. This ensures that the value of the most recently assigned
field is consistent across the union.

For more information, see :ref:`union-reference` reference.

Customazation
-------------


You can further customize the behavior of unions by implementing a custom :class:`~caterpillar.model.UnionHook`.
This allows you to define additional actions or modifications when fields in a union
are accessed or changed.

To do this, you can specify the :code:`hook_cls` parameter in the union decorator, which
takes a custom hook class that will manage the synchronization and processing of
the union's fields.

.. code-block:: python
    :caption: Custom UnionHook class

    @union(hook_cls=MyCustomUnionHook)
    class ChunkName:
        text: Bytes(4)
        options: ChunkOptions
