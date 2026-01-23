.. _tutorial-basics_context:

*******
Context
*******

In *Caterpillar*, the context is a special feature that keeps track of the current
packing or unpacking process. The context allows you to reference the current object
being packed or parsed using the special variable :code:`this`. It also provides
access to the parent object, if applicable, through the variable :code:`parent`.

The context is useful when defining structs that depend on other fields' values.
For example, you can reference the length of a string field and use it to define
the length of another field dynamically.

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :caption: Understanding the *context*

            @struct
            class Format:
                length: uint8
                foo: CString(this.length)   # <-- just reference the length field

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :caption: Understanding the *context*

            @struct
            class Format:
                length: uint8_t
                foo: f[str, CString(this.length)]   # <-- just reference the length field

Runtime Length of Objects
~~~~~~~~~~~~~~~~~~~~~~~~~

In certain cases, you may need to retrieve the runtime length of a variable within
the context of the current object. The special class :code:`lenof` provides this
functionality. It applies the :code:`len()` function to the object you're referencing
and returns the length.

Context Paths
~~~~~~~~~~~~~

You can use context paths to access elements of a sequence or nested structures. For
example, if you have a field :code:`foobar` that is a sequence, you can access its
elements like this:

>>> path = this.foobar[0]  # Access elements of a sequence within the current context
Path('_obj.foobar', getitem(0))
>>> path(context)
...


Custom Context Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To apply a custom context class that conforms to the current
:class:`_ContextLike` protocol definition. For instance, packing
and unpacking can be faster if the C-extension implemetation of
the :code:`Context` class is used.

>>> from caterpillar.context import O_CONTEXT_FACTORY
>>> from caterpillar.c import c_Context
>>> O_CONTEXT_FACTORY.value = c_Context