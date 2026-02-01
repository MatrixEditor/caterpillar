.. _library_model_bitfield:

========
Bitfield
========

.. versionchanged:: 2.5.0
    New revised concept since v2.5.0.

.. py:currentmodule:: caterpillar.model

Each Bitfield instance maintains a sequence of bitfield groups, where each group
contains a collection of sized fields. A bitfield group may consist of either multiple
entries (i.e., any types that can be converted to an integral type) or a single
_StructLike object. For example, consider the following bitfield definition:

.. code-block:: python

  @bitfield
  class Format:
      a1: 1
      a2: 1 - boolean
      _ : 0
      b1: char
      c1: uint32

This Bitfield definition will generate three distinct bitfield groups (labeled here as
groups a, b, and c). By default, bitfields use 8-bit alignment, leading to the following
layout:

.. code-block::

       Group      Pos       Bits
       a          0x00      8
       b          0x01      8
       c          0x02      32

Internally, only the first group requires special bit-level parsing. The remaining groups
(b and c) are treated as standard structures since they span full bytes or words without
sub-byte alignment. This dynamic grouping mechanism allows leveraging full struct-like
class definitions within bitfields.

This new approach enables more complex and expressive bitfield definitions. The annotation
syntax is therefore extended as follows:

.. code-block:: text

       +---------------------------------------------------+--------------------------------------+
     1.| <name> : <bits> [ - <field> ]                     | Standard field with optional type    |
       +---------------------------------------------------+--------------------------------------+
     2.| <name> : 0                                        | Aligns to the next byte boundary     |
       +---------------------------------------------------+--------------------------------------+
     3.| <name> : <field>                                  | Struct-like field (no bits consumed) |
       +---------------------------------------------------+--------------------------------------+
     4.| <name> : (<field>,<factory>)                      | Field with custom type factory       |
       +---------------------------------------------------+--------------------------------------+
     5.| <name> : (<bits>,<factory>[,<options>])           | bits with custom type factory        |
       |        : (<bits>,[<options>])                     | and options                          |
       +---------------------------------------------------+--------------------------------------+


Main Interface
--------------

.. autoclass:: Bitfield
    :members:

    .. versionchanged:: 2.5.0
        Updated concept. See the :ref:`datamodel_standard_bitfield` reference for more information.

.. autoclass:: BitfieldGroup
    :members:

    .. versionchanged:: 2.5.0
        Renamed from ``BitFieldGroup`` to ``BitfieldGroup``

.. autoclass:: BitfieldEntry
    :members:

    .. versionadded:: 2.5.0


.. autofunction:: getbits

.. autofunction:: issigned

.. autofunction:: bitfield

    .. versionchanged:: 2.5.0
        Added the ``alignment`` parameter.

Default Factory Classes
-----------------------

.. autoclass:: BitfieldValueFactory
    :members:

    .. versionadded:: 2.5.0

.. autoclass:: CharFactory
    :members:

    .. versionadded:: 2.5.0

.. autoclass:: EnumFactory
    :members:

    .. versionadded:: 2.5.0


Default Options
---------------

.. py:attribute:: EndGroup

    .. versionadded:: 2.5.0

    Alias for the :attr:`B_GROUP_NEW` flag, used to indicate that a new bitfield group should be started.


.. py:attribute:: NewGroup

    Alias for the :attr:`B_GROUP_END` flag, used to indicate that the current bitfield group should be finalized.


.. autoclass:: SetAlignment
    :members:

Bitfield Mixins
---------------

.. autoclass:: caterpillar.model.BitfieldDefMixin
    :private-members: __struct__
    :members:

.. autoclass:: caterpillar.model.bitfield_factory
    :members: