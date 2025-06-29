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
of elements. We can attempt to simulate a chain of extended *base sequences* using the
concatenation of two sequences. The :meth:`~sequence.__add__` method will *import* all fields
from the other specified sequence. The only disadvantage is the placement required by the
operator. For instance:

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
    This will alter the *BaseFormat* sequence, making it unusable elsewhere as the *base* for
    all sub-sequences. Therefore, it is not recommended to use inheritance within sequences.
    The :class:`~caterpillar.model.Struct` class resolves this issue with ease.

Nesting sequences is allowed by default and can be achieved by incorporating another
:class:`~caterpillar.model.Sequence` into the model. It is important to note that *nesting* is distinct from
*inheritance*, adding an additional layer of packing and unpacking.

>>> Format = Sequence({"other": BaseFormat, "b": uint32})
