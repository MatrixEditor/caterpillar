.. _changelog:

*********
Changelog
*********

*More entries will be added in the future.*

.. _changelog_2.5.0:

2.5.0
=====

This version introduces massive changes due to the addition of stub files. Most of the type hints in the Python
file are ported into several stub files. Additionally, the bitfield concept was completely renewed to be more
flexible and dynamic.

Added
-----

*caterpillar.abc*
^^^^^^^^^^^^^^^^^

- :class:`_SupportsBits` protocol
- :class:`_ContainsBits` protocol
- :class:`_SupportsType` protocol

*caterpillar.shortcuts*
^^^^^^^^^^^^^^^^^^^^^^^

- New shortcuts: :func:`typeof`, :func:`to_struct`, :func:`hasstruct`, :func:`getstruct` and :func:`sizeof`

*caterpillar.shared*
^^^^^^^^^^^^^^^^^^^^

- New constants from other modules: :attr:`ATTR_BYTEORDER`, :attr:`ATTR_TYPE`, :attr:`ATTR_BITS`, :attr:`ATTR_SIGNED`, :attr:`ATTR_TEMPLATE`

*caterpillar.context*
^^^^^^^^^^^^^^^^^^^^^

- New context attribute: `_root` can be set to point to the root context instance. Internally, instead of a for-loop that iterates through parent context instances, a simple :code:`self.get(...)` call is made.

.. raw:: html

    <hr>

Removed
-------

*caterpillar.abc*
^^^^^^^^^^^^^^^^^

- ``_Action`` protocol and create two separate Protocols that form::

    _ActionLike = _SupportsActionUnpack | _SupportsActionPack

- ``__type__`` requirement from :class:`_StructLike`
- **Breaking:** ``_EnumLike``, ``_ContextPathStr``

*caterpillar.model*
^^^^^^^^^^^^^^^^^^^

- Unused ``getformat`` function

*caterpillar.fields.common*
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Unused ``__fmt__`` function in :class:`Transformer`

.. raw:: html

    <hr>

Changed
-------

*caterpillar.abc*
^^^^^^^^^^^^^^^^^

- Rename ``_Switch`` protocol to :attr:`_SwitchLike`
- Move the following attributes and methods into *caterpillar.shared*: rename ``STRUCT_FIELD`` to :attr:`ATTR_STRUCT`, :func:`hasstruct`, :func:`getstruct` and :func:`typeof`

*caterpillar.byteorder*
^^^^^^^^^^^^^^^^^^^^^^^

- Move ``BYTEORDER_FIELD`` to *caterpillar.shared* as :attr:`ATTR_BYTEORDER`


*caterpillar.model*
^^^^^^^^^^^^^^^^^^^

- :func:`sizeof` now checks if the provided object implements the :class:`_SupportsSize` protocol
- New :class:`Bitfield` concept with enhanced syntax

.. raw:: html

    <hr>

Fixed
-----

*caterpillar.model*
^^^^^^^^^^^^^^^^^^^

- when parsing union objects with an unbound stream object
- field options defined in Sequences and Structs were not populated when creating fields.
