.. _union-reference:

Union
=====

Internally constructing unions in the library poses challenges. The current implementation uses
the predefined behavior of the :class:`~caterpillar.model.Sequence` class for union types. It selects the field with
the greatest length as its representational size. *Unions*, much like *BitFields*, must store a static
size.

**In essence, they behave similarly to C unions.** A traditional function hook will be installed on
the model to capture field assignments. What that means will be illustrated by the following example:

.. code-block:: python

    >>> @union
    ... class Format:
    ...     foo: uint16
    ...     bar: uint32
    ...     baz: boolean
    ...
    >>> obj = Format()      # union does not need any values

Right now, all attributes store the default value (:code:`None`). If we assign a new value to one field, it
will be applied to all others. Hence,

>>> obj.bar = 0xFF00FF00

will result in

.. code-block:: python

    >>> obj
    Format(foo=65280, bar=4278255360, baz=False)


.. admonition:: Implementation Detail

    The constructor is the only place where there is no synchronization between fields. Additionally, the current
    implementation may produce some overhead, because every *refresh* will first pack the new value and then
    executes *unpack* on all other fields.