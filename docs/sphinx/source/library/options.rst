.. _options:

****************
Options / Flags
****************

This library provides a flexible system of options and flags to control various aspects
of data structures, serialization, and deserialization behaviors. Options can be set
globally or applied to specific types to fine-tune performance, memory usage, and
structure representation.

Options by Type
---------------

Options are grouped by the type of object they affect.

Global Options
^^^^^^^^^^^^^^

.. attribute:: caterpillar.options.O_ARRAY_FACTORY

   Specifies a factory function or class for creating array instances. This allows you
   to replace the default array type with a more efficient or specialized implementation.
   For example, you can use :code:`numpy.ndarray` for large numeric arrays to reduce
   memory usage:

   .. code-block:: python

      from caterpillar.options import O_ARRAY_FACTORY
      from numpy import array

      # Set the array factory globally
      O_ARRAY_FACTORY.value = array

   With this configuration, unpacked arrays will use the specified factory, potentially
   leading to significant memory savings. The following table demonstrates the memory
   footprint of unpacked objects under different configurations:

   .. list-table:: Object sizes for different configuration options
      :header-rows: 1
      :stub-columns: 1
      :widths: 10, 15, 15

      * - Configuration
        - :code:`formats/nibarchive`
        - :code:`formats/caf` [*]_
      * - Default configuration
        - 26520
        - 10608
      * - :code:`__slots__` classes
        - 14240
        - 3848
      * - Default configuration with :code:`numpy.ndarray`
        - 7520
        - 1232
      * - :code:`__slots__` classes with :code:`numpy.ndarray`
        - 6152
        - 384
      * - Original file size
        - **1157**
        - **5433**

.. [*] A CAF audio file may include a chunk that contains only zeroed data. By ignoring
   this chunk during unpacking, the in-memory size can be smaller than the original file.

Sequence Options
^^^^^^^^^^^^^^^^

.. note::

   All sequence-related options also apply to structs.

.. attribute:: caterpillar.options.S_DISCARD_UNNAMED

   When enabled, this option discards all *unnamed* fields from the final unpacked result.
   An *unnamed* field must follow the convention:

   .. code-block:: bnf

      <unnamed> := '_' [0-9]*

   This allows you to include padding or other non-essential fields without polluting
   the output. For example:

   .. code-block:: python
      :caption: Sequence with an unnamed field

      >>> schema = Seq({
      ...     "a": uint8,
      ...     "_": padding[10]
      ... }, options={opt.S_DISCARD_UNNAMED})
      >>> data = b"\xFF" + bytes(10)
      >>> unpack(schema, data)
      {'a': 255}
      >>> pack(_, schema)
      b'\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

.. data:: caterpillar.options.S_DISCARD_CONST

   Discards all constant fields from the final result. This is useful for fields
   that serve only validation or padding purposes.

Struct Options
^^^^^^^^^^^^^^

.. data:: caterpillar.options.S_SLOTS

   When enabled, this option generates a struct class with a :code:`__slots__` declaration.
   Using :code:`__slots__` significantly reduces the per-object memory overhead by preventing
   the creation of an instance :code:`__dict__`. For example:

   .. code-block:: python

      @struct
      class DictClass:
          a: uint8
          b: uint8
          c: uint8
          d: uint8
          e: uint8
          f: uint8
          g: uint8

      @struct(options={opt.S_SLOTS})
      class SlotsClass:
          a: uint8
          b: uint8
          c: uint8
          d: uint8
          e: uint8
          f: uint8
          g: uint8

   Comparing memory usage using `pympler <https://pympler.readthedocs.io/en/latest/>`_:

   .. code-block:: python
      :caption: Memory usage difference with :code:`__slots__`

      >>> o1 = DictClass(*[0xFF]*7)
      >>> asizeof.asizeof(o1)
      712
      >>> o2 = SlotsClass(*[0xFF]*7)
      >>> asizeof.asizeof(o2)
      120

   The class definition itself also occupies less memory:

   .. code-block:: python

      >>> from sys import getsizeof
      >>> getsizeof(DictClass)
      1704
      >>> getsizeof(SlotsClass)
      936

.. data:: caterpillar.options.S_REPLACE_TYPES

   Replaces field types in the class annotations with their native Python equivalents.
   This option is primarily intended for documentation purposes. It removes all
   :class:`caterpillar.fields.Field` instances from annotations. For example:

   .. code-block:: python

      @struct
      class Format:
          a: uint8
          b: String(10)
          c: Uuid

      # Enable type replacement globally
      opt.set_struct_flags(opt.S_REPLACE_TYPES)
      # Or apply it directly:
      @struct(options={opt.S_REPLACE_TYPES})

   Comparison of annotations:

   .. code-block:: python

      >>> Format.__annotations__ # Without replacement
      {'a': <FormatField(int) 'B'>, 'b': <String>, 'c': <Uuid>}
      >>> Format.__annotations__ # With replacement
      {'a': <class 'int'>, 'b': <class 'str'>, 'c': <class 'uuid.UUID'>}

.. data:: caterpillar.options.S_EVAL_ANNOTATIONS

   Ensures that annotations are evaluated at runtime if you use
   :code:`from __future__ import annotations`. When enabled, stringified annotations
   are evaluated before analysis.

   .. caution::

      Use with care! Evaluating annotations can lead to the execution of untrusted code.

.. data:: caterpillar.options.S_UNION

   Internal option that enables union behavior for the :class:`caterpillar.model.Struct` class.

Field Options
^^^^^^^^^^^^^

.. attribute:: caterpillar.options.F_KEEP_POSITION

   When enabled, this option retains the position information of each field in the
   serialized data. This is the default behavior.

.. attribute:: caterpillar.options.F_DYNAMIC

   Marks the field as dynamic, indicating that its size or format is determined at
   runtime rather than being statically defined. This is used internally to support
   advanced features like variable-length fields.

   .. deprecated:: 2.8.0
      No longer used directly, but still supported.

.. attribute:: caterpillar.options.F_SEQUENTIAL

   Indicates that this field should be processed sequentially relative to other
   fields, ensuring that order-dependent parsing or packing logic is respected.
   This is primarily for internal use in complex layouts.

   .. deprecated:: 2.8.0
      No longer used directly.

.. attribute:: caterpillar.options.F_OFFSET_OVERRIDE

   Allows you to override the calculated offset for this field within its parent
   structure. This means, the offset used by the :meth:`struct.__matmul__`
   operation will be used from here on.


Bit-field Options
^^^^^^^^^^^^^^^^^

Bit-field options provide fine-grained control over the alignment, grouping,
and interpretation of individual fields and entire bit-field classes.


.. attribute:: caterpillar.options.B_OVERWRITE_ALIGNMENT

   Replaces the current alignment with the alignment explicitly defined by the field.
   This option is applicable only to fields within a bit-field class.

   For example, the following structure overrides the default alignment of 8 bits
   with a 32-bit alignment for the specified field:

   .. code-block:: python

      @bitfield
      class Format:
          # Override alignment from 8 bits to 32 bits
          a: 4 - uint32 | B_OVERWRITE_ALIGNMENT


   .. versionadded:: 2.5.0

.. attribute:: caterpillar.options.B_GROUP_END

   Adds the annotated field to the current bit-field group and immediately aligns
   the group's total size according to the active alignment constraints.
   This option is applicable only to fields.

   For example, to avoid automatic alignment to the next multiple of 16 bits:

   .. code-block:: python

      @bitfield
      class Format:
          a1: 4
          a2: 3
          # Prevent automatic alignment to 16 bits:
          a3: (1, B_GROUP_END)
          b1: 1
          ...

   .. versionadded:: 2.5.0

.. attribute:: caterpillar.options.B_GROUP_NEW

   Finalizes the current bit-field group by aligning it, then starts a new group
   and adds the annotated field to this new group.
   This option is applicable only to fields.

   Example usage where a new group is started with its own alignment:

   .. code-block:: python

      @bitfield
      class Format:
          a1: 4
          a2: 4
          # Finalize current group and start new one with 8-bit alignment:
          b1: (1, B_GROUP_NEW)

   .. versionadded:: 2.5.0

.. attribute:: caterpillar.options.B_GROUP_KEEP

   *Applicable only to classes.*

   When applied at the class level, this option instructs the bit-field structure
   to preserve existing group alignments throughout parsing and packing.
   It affects how alignment statements are interpreted within the class body.

   .. versionadded:: 2.5.0

.. attribute:: caterpillar.options.B_NO_AUTO_BOOL

   *Applicable only to classes.*

   Prevents the automatic assignment of a boolean type factory for fields
   that are exactly one bit in size. By default, one-bit fields are treated
   as boolean values; enabling this option disables that behavior, preserving
   the raw integer representation instead.

   .. versionadded:: 2.5.0




Interface
---------

.. autoclass:: caterpillar.options.Flag
    :members:

.. autofunction:: caterpillar.options.configure

.. autofunction:: caterpillar.options.set_struct_flags

.. autofunction:: caterpillar.options.set_field_flags

.. autofunction:: caterpillar.options.set_union_flags

.. autofunction:: caterpillar.options.get_flags

.. autofunction:: caterpillar.options.has_flag

.. autofunction:: caterpillar.options.get_flag

