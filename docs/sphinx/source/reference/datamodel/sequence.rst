.. _datamodel_standard_sequence:

Sequence
========

A sequence functions independently of fields. The library introduces the :class:`~caterpillar.model.Sequence`
as a named finite collection of :class:`~caterpillar.fields.Field` objects. A *Sequence*
operates on a model, which is a string-to-field mapping by default. Later, we will discuss
the distinctions between a *Sequence* and a *Struct* regarding the model representation.

A sequence definition entails the specification of a :class:`~caterpillar.model.Sequence` object by directly
indicating the model to use. Inheritance poses a challenge with sequences, as they are not
designed to operate on a type hierarchy. The default instantiation with all default options
involves passing the dictionary with all fields directly:

>>> Format = Sequence({"a": uint8, "b": uint32})

.. admonition:: Programmers Note:

    All sequence types introduced by this library can also store so-called *unnamed* fields.
    These fields are not visible in the unpacked result and are automatically packed, removing
    concerns about them when the option ``S_DISCARD_UNNAMED`` is active. Their names usually
    begin with an underscore and must solely contain numbers (e.g., :code:`_123`).

The sequence follows the :class:`~caterpillar.fields.Field` configuration model, allowing sequence and
field-related options to be set. As mentioned earlier, the ``S_DISCARD_UNNAMED`` option can
be used for example to exclude all unnamed fields from the final representation. A complete
list of all configuration options and their impact can be found in :ref:`options`.

All sequences store a configurable :class:`ByteOrder` and :class:`Arch` as architecture,
which are passed to **all** fields in the current model. For more information on why these
classes are not specified as an enum class, please refer to :ref:`byteorder`.

Inheritance in sequences is intricate, as a :class:`~caterpillar.model.Sequence` is constructed from a dictionary
of elements and has no Python type hierarchy. The legacy ``+`` and ``-`` operators mutate the
left-hand sequence by importing or removing fields in its internal representation. They are kept
for compatibility and can be useful for one-off transformations, but they are not safe base-sequence
composition helpers. For instance:

.. code-block:: python

    >>> BaseFormat = Sequence({"magic": b"MAGIC", "a": uint8})
    >>> Format = Sequence({"b": uint32, "c": uint16}) + BaseFormat

will result in the following field order:

.. code-block:: python

    >>> list(Format.get_members())
    ['b', 'c', 'magic', 'a']

which is not the intended order. The correct order should be :code:`['magic', 'a', 'b', 'c']`.
This can be achieved by using the :code:`BaseFormat` instance as the first operand.

.. warning::
    Using ``BaseFormat + Extension`` will alter the *BaseFormat* sequence, making it unusable
    elsewhere as the unchanged base for other formats. Prefer ``merged`` and ``without`` for
    reusable sequence composition, or use :class:`~caterpillar.model.Struct` when the format
    naturally follows a type hierarchy.

For non-mutating composition, use :meth:`~caterpillar.model.Sequence.merged`
and :meth:`~caterpillar.model.Sequence.without`. These helpers clone imported
field wrappers and leave the original sequences unchanged:

.. code-block:: python

    >>> BaseFormat = Sequence({"magic": b"MAGIC", "a": uint8})
    >>> Extension = Sequence({"b": uint32})
    >>> Format = BaseFormat.merged(Extension)
    >>> list(BaseFormat.get_members())
    ['magic', 'a']
    >>> list(Format.get_members())
    ['magic', 'a', 'b']

``merged`` starts with a clone of the receiver and imports clones from each
additional sequence. Duplicate field names from later sequences replace earlier
ones in-place in the returned layout. ``without`` starts with a clone of the
receiver and removes fields by name, again leaving all source sequences intact.

Nesting sequences is allowed by default and can be achieved by incorporating another
:class:`~caterpillar.model.Sequence` into the model. It is important to note that *nesting* is distinct from
*inheritance*, adding an additional layer of packing and unpacking.

>>> Format = Sequence({"other": BaseFormat, "b": uint32})
