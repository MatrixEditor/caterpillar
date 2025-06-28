.. _datamodel_standard_struct:

Struct
======

A *struct* describes a finite collection of named fields. In contrast to a *sequence*, a *struct*
utilizes Python classes as its model. The annotation feature in Python enables the definition of
custom types as annotations, enabling this special struct class to create a model solely based on
class annotations. Additionally, it generates a ``dataclass`` of the provided model, offering a
standardized string representation.

Several differences exist between a :class:`~caterpillar.model.Sequence` and a
:class:`~caterpillar.model.Struct`, with the most significant ones highlighted below:


.. list-table:: Behaviour of structs and sequences
    :header-rows: 1
    :widths: 10, 15, 15
    :stub-columns: 1

    * -
      - Sequence
      - Struct
    * - Model Type
      - dict
      - type
    * - Inheritance
      - No
      - Yes
    * - Attribute Access
      - :code:`x["name"]`
      - :code:`getattr(x, "name", None)`
    * - Unpacked Type (also needed to pack)
      - dict [*]_
      - instance of model
    * - Documentation
      - No
      - Yes


.. [*] The unpacked values are stored inside a :class:`~caterpillar.context.Context` instance, a direct subclass of a dictionary.

As evident from the comparison, the :class:`~caterpillar.model.Struct` class introduces new features such as
inheritance and documentation support. It's crucial to note that inheritance uses
struct types exclusively.

The :class:`~caterpillar.model.Sequence` class implements a specific process for creating an internal representation
of the given model. The :class:`~caterpillar.model.Struct` class enhances this process by handling default values, replacing
types for documentation purposes, or removing annotation fields directly from the model. Additionally,
this class adds :attr:`~class.__struct__` to the model afterward.

.. admonition:: Implementation Note

    If you decide to use the ``annotation`` feature from the ``__future__`` module, it is necessary to
    enable :attr:`~options.S_EVAL_ANNOTATIONS` since it "`Stringizes`_" all annotations. ``inspect`` then
    evaluates all strings, introducing a potential security risk. Exercise with caution when evaluating code!

Specifying structs is as simple as defining `Python Classes`_:

.. code-block:: python

    >>> @struct
    ... class BaseFormat:
    ...     magic: b"MAGIC"
    ...     a: uint8
    ...

Internally, a representation with all required fields and their corresponding names is
created. As :code:`b"MAGIC"` or :code:`uint8` are instances of types, the type replacement
for documentation purposes should be enabled, as shown in :ref:`struct_type`.

As described above, this class introduces an easy-to-use inheritance system using the method
resolution order of Python:

.. code-block:: python

    >>> @struct
    ... class Format(BaseFormat):
    ...     b: uint32
    ...     c: uint16
    ...
    >>> list(Format.__struct__.get_members())
    ['magic', 'a', 'b', 'c']

.. admonition:: Programmers Note

    As the :class:`~caterpillar.model.Struct` class is a direct subclass of :class:`~caterpillar.model.Sequence`, nesting is supported
    by default. That means, so-called *anonymous inner* structs can be defined within a class
    definition.

    .. code-block:: python

        >>> @struct
        ... class Format:
        ...     a: uint32
        ...     b: {"c": uint8}
        ...

    It is not recommended to use this technique as the inner structs can't be used anywhere else.
    Anonymous inner union definitions are tricky and are not officially supported yet. There are
    workarounds to that problem, which are discussed in the API documentation of :class:`~caterpillar.model.Sequence`.

