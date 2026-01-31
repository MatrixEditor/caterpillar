.. _tutorial-bitfield:

Bitfields
=========

*Bitfields* are a compact way to pack multiple fields into a fixed-size binary
representation while also allowing dynamic structs in-between.

.. versionchanged:: 2.5.0

    Completely reworked the concept of a *Bit-field*. The reference explains the
    new concept and its implementation rules in detail: :ref:`datamodel_standard_bitfield`.

    In short, the new system supports:

    - Dynamic grouping: Each Bitfield can have multiple *dynamic* bitfield groups.
    - Struct-like fields: Full struct classes can be embedded.
    - **Custom alignment and type factories.**
    - Flexible syntax with 5 powerful rules.


Core Concepts
-------------

Each Bitfield instance contains one or more *bitfield groups*. A
group is simply a collection of *bitfield entries* that are packed together based on
alignment constraints or a single :class:`~caterpillar.fields.Field`.

How it works: Groups and Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you define a Bitfield class, each field line describes either a simple bit-sized
entry or a more complex structure. The fields are automatically grouped based on pre-defined
syntax definitions and processing rules.

Here is the general idea:

- Bitfield groups collect fields until the group is finalized (e.g. because of an alignment boundary or a struct-like field).
- Within a group, fields may consume only part of a byte, or a whole number of bytes.
- Once a group is finalized, any new fields start a new group.

This approach means you don't have to manually calculate where each field starts and ends. Instead,
the system infers layout while giving you the tools to align fields precisely when needed. Neat, isn't it?


The Syntax
----------

Each field is defined using one of five patterns:

1. Basic fixed-size bits field:

   A standard field defines a name and the number of bits it occupies. Example:



.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python

            @bitfield
            class Format:
                flag : 1 # means the field flag uses 1 bit.


    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python

            @bitfield
            class Format:
                flag : f[int, 1] # means the field flag uses 1 bit.
                # or using a type
                flag : int1_t

2. Basic fixed-size bits field with type from struct:

   You can specify how the bits should be interpreted using a type that will be
   resolved from the given struct using the :class:`_SupportsType` protocol:


.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python

            @bitfield
            class Format:
                valid : 1 - boolean # the 1-bit field should be interpreted as a bool

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python

            @bitfield
            class Format:
                # the 1-bit field should be interpreted as a bool
                valid : f[bool, 1 - boolean]


3. Alignment:

   If you define a field with a size of ``0``, it forces the Bitfield to align the current group
   to the next byte boundary. Afterwards, the current group is finalized and a new one is started.
   To use the automatic alignment in the extended syntax, use :attr:`balign_t`.


.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python

                @bitfield
                class Format:
                    flag  : 1
                    _     : 0 # align to 8bits
                    valid : 1 - boolean        # size will be 2x 8bits

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python

                @bitfield
                class Format:
                    flag  : int1_t
                    _     : balign_t = Invisible() # align to 8bits
                    valid : f[bool, 1 - boolean]  # size will be 2x 8bits

4. Struct-like Field:

   You can embed an entire struct-like class inside the Bitfield. (Any object conforming to the
   :class:`_StructLike` protocol).

5. Custom Factory with Options:

   For advanced cases, you can specify not only the number of bits and a factory (a type converter)
   but also additional options to fine-tune grouping or alignment:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python

            @bitfield
            class Format:
                # 7bits, converted to char and alignment set to 24bits
                name : (7, CharFactory, SetAlignment(24))

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python

            @bitfield
            class Format:
                # 7bits, converted to char and alignment set to 24bits
                name : f[str, (7, CharFactory, SetAlignment(24))]

Practical Example
-----------------

One practical example of using BitFields is implementing the chunk-naming convention
for PNG files. Here's how you might define the options for a chunk using a bitfield structure:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :caption: Implementing the `chunk-naming <https://www.w3.org/TR/png/#5Chunk-naming-conventions>`_ convention

            @bitfield(opions={S_DISCARD_UNNAMED})
            class ChunkOption:
                _     : 2               # <-- first two bits are not used
                value : 1               # automatically boolean

            @struct
            class ChunkOptions:
                ancillary    : ChunkOption # f0
                private      : ChunkOption # f1
                reserved     : ChunkOption # f2
                safe_to_copy : ChunkOption # f3

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :caption: Implementing the `chunk-naming` convention

            @bitfield(opions={S_DISCARD_UNNAMED})
            class ChunkOption:
                _     : f[None, 2] = Invisible() # <-- first two bits are not used
                value : int1_t                   # automatically boolean

            @struct
            class ChunkOptions:
                ancillary    : ChunkOption # f0
                private      : ChunkOption # f1
                reserved     : ChunkOption # f2
                safe_to_copy : ChunkOption # f3

In the example above, each field within the :code:`ChunkOptions` class is assigned
8bits according to the :code:`ChunkOption` bitfield.

- The first two bits (:code:`_`) are unused (or "unnamed").
- The :code:`value` field uses 1 bit, representing a flag (automatically boolean type).
- all other bits are ignored automatically

Here's a breakdown of how the bits are laid out in memory:

.. code-block:: text

    byte     :     0        1       2        3
    bit      : 76543210 76543210 76543210 76543210
    ----------------------------------------------
    breakdown: 00100000 00100000 00100000 00100000
               ├┘│└─┬─┘ ├┘│└─┬─┘ ├┘│└──┬┘ ├┘│└─┬─┘
               u f0 a   u f1 a   u f2  a  u f3 a

Where:
- :code:`u` = unnamed bits (unused)
- :code:`a` = added bits
- :code:`f0`, :code:`f1`, :code:`f2`, :code:`f3` = corresponding fields (`ancillary`, `private`, `reserved`, `safe_to_copy`)

Each bit or group of bits is allocated to a specific field, allowing you to
pack multiple flags or small values into a single byte or a group of bytes.


