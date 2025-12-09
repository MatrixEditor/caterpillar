.. _changelog:

*********
Changelog
*********

*More entries will be added in the future.*

.. _changelog_2.6.3:

[2.6.3] - Patch
===============

Fixed
-----

*caterpillar*
^^^^^^^^^^^^^^^^^^^^^^^^^

- Fix various stub files and decorator annotations


.. _changelog_2.6.2:

[2.6.2] - Patch
===============

Fixed
-----

*caterpillar.field._base*
^^^^^^^^^^^^^^^^^^^^^^^^^

- Fix 1-length sized array fields

*caterpillar*
^^^^^^^^^^^^^

- Add compatibility with at least Python 3.10 by using ``typing_extensions``


.. _changelog_2.6.1:

[2.6.1] - Hot-Fix
=================

Fixed
-----

*caterpillar.fields._base*
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Fix switch functionality within the `Field` class for `ContextPath` objects

*caterpillar.fields.common*
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- fix ``%`` operator for the :class:`~caterpillar.fields.common.AsLengthRef` class.


.. _changelog_2.6.0:

[2.6.0] - Minor Release
=======================

Added
-----

*caterpillar.fields._base*
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Add support for non-context lambda switch fields


*caterpillar.fields.common*
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Add compatibility support for CAPI atoms in ``Int``, ``UInt`` and
  ``PyStructFormattedField``
- Add new :class:`~caterpillar.fields.common.AsLengthRef` class

*caterpillar.options*
^^^^^^^^^^^^^^^^^^^^^

- Add custom ``Flag.__eq__`` implementation to support equality check with ``c_Option`` objects


*caterpillar.abc*
^^^^^^^^^^^^^^^^^

- Add new typing-only `_OptionLike` protocol
- Add missing `_SupportsType` protocol to the stubs file
- Add new method `get` to the `_ContextLike` protocol


*caterpillar.context*
^^^^^^^^^^^^^^^^^^^^^

- Add new option :py:attr:`~caterpillar.context.O_CONTEXT_FACTORY` that controls
  the global context type. Value must be a method or another type implementing
  the :class:`_ContextLike` protocol
- Add new global context path: :py:attr:`~caterpillar.context.root` (exported as ``G`` in shortcuts)

*caterpillar.shortcuts*
^^^^^^^^^^^^^^^^^^^^^^^

- Add new shortcuts ``C`` for :py:attr:`~caterpillar.context.ctx`, ``P`` for
  :py:attr:`~caterpillar.context.parent` and ``G`` for the
  :py:attr:`~caterpillar.context.root` context as
  :class:`~caterpillar.context.ContextPath` objects


*CAPI*
^^^^^^

- New index assignment system when generating CAPI code. A running number is now
  applied instead of a hard coded index.
- Add *complete* Context implementation in C (:class:`c_Context`) that conforms
  to the :class:`_ContextLike` protocol.
- Add :class:`Atom` for C-based struct-like classes. This class was previously
  known as :class:`catom`
- Add native support for `__bits__` in :class:`Atom`
- Add special class :class:`LengthInfo` for packing or unpacking multiple objects
- New builtin atoms (CAPI): :class:`Repeated`, :class:`Conditional` and :class:`Switch`
- Add new shared objects and exception types to the native implementation
  (:c:var:`Cp_ContextFactory`, :c:var:`Cp_ArrayFactory`, :c:var:`CpExc_Stop` and
  :c:var:`Cp_DefaultOption`)


Changed
-------

*caterpillar.fields._base*
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Rework :class:`~caterpillar.fields._base.Field` implementation to reduce
  overhead when packing and unpacking elements
- Use pre-computed states instead of calculating everything on-the-fly. States
  will be adjusted when setting new values (automatically updated through
  :code:`@property` attributes)


Fixed
-----

*caterpillar.fields.common*
^^^^^^^^^^^^^^^^^^^^^^^^^^^

+ Fix issue in Prefixed that occurred when the internal struct packs a sequence
  of elements

Removed
-------

*CAPI*
^^^^^^

- Remove old CAPI and completely revamp the CAPI concept to make it compatible
  to the Python equivalent.


.. _changelog_2.5.1:

[2.5.1] - Hot-Fix Release
=========================

Fixed
-----

*caterpillar.model*
^^^^^^^^^^^^^^^^^^^

- An issue when packing or unpacking a bitfield with unnamed fields AND :attr:`S_DISCARD_UNNAMED` enabled


.. _changelog_2.5.0:

[2.5.0] - Minor Release
=======================

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


*Documentation*
^^^^^^^^^^^^^^^

- Update reference and library docs as well as section numbering

.. raw:: html

    <hr>

Fixed
-----

*caterpillar.model*
^^^^^^^^^^^^^^^^^^^

- when parsing union objects with an unbound stream object
- field options defined in Sequences and Structs were not populated when creating fields.
