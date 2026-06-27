.. _model:

************
Struct Model
************

The model package contains the high-level building blocks used to describe
binary layouts: :class:`~caterpillar.model.Sequence` for mapping-based layouts,
:class:`~caterpillar.model.Struct` for class-based layouts,
:class:`~caterpillar.model.Bitfield` for bit-level groups, and templates for
deriving families of related structures.

These model types implement the same pack, unpack, size, and type protocols
used by primitive fields, so they can be nested or wrapped in
:class:`~caterpillar.fields.Field` objects.

.. toctree::
    :maxdepth: 2

    model/sequence
    model/struct
    model/bitfield
    model/template
