.. _tutorial-bitfield:

Bitfields
=========

.. attention::
    This section is still under development.

**BitFields** are a specialized feature in *Caterpillar* that allow you to define
fields at the bit level within a struct. This is particularly useful when dealing
with compact binary formats, such as network protocols, file formats, or hardware
interfaces where each bit has a specific meaning.

BitFields allow you to specify the number of bits allocated for each field and
provide the ability to fine-tune how data is stored and retrieved from a binary
stream. This feature is useful when you need to work with bit-level manipulations,
such as when defining flags, options, or small data values packed into a single
byte or multiple bytes.

Syntax
------

In *Caterpillar*, BitFields are defined using the :code:`@bitfield` decorator, and the
individual fields are specified with their respective bit widths.

One practical example of using BitFields is implementing the chunk-naming convention
for PNG files. Here's how you might define the options for a chunk using a bitfield structure:

.. code-block:: python
    :caption: Implementing the `chunk-naming <https://www.w3.org/TR/png/#5Chunk-naming-conventions>`_ convention

    @bitfield(options={S_DISCARD_UNNAMED})
    class ChunkOptions:
        _            : 2        # <-- first two bits are not used
        ancillary    : 1        # f0
        _1           : 0
        _2           : 2
        private      : 1        # <-- the 5-th bit (from right to left)
        _3           : 0
        _4           : 2
        reserved     : 1        # f2
        _5           : 0        # <-- padding until the end of this byte
        _6           : 2
        safe_to_copy : 1        # f3


In the example above, each field within the :code:`ChunkOptions` class is assigned
a specific number of bits:

- The first two bits (:code:`_`) are unused (or "unnamed").
- The :code:`ancillary` field uses 1 bit, representing a flag.
- Other fields like :code:`private`, :code:`reserved`, and :code:`safe_to_copy` are allocated 1 or 2 bits as needed.

Here's a breakdown of how the bits are laid out in memory:

.. code-block:: text

    byte     :     0        1       2        3
    bit      : 76543210 76543210 76543210 76543210
    ----------------------------------------------
    breakdown: 00100000 00100000 00100000 00100000
               \/|\___/ \/|\___/ \/|\___/ \/|\___/
               u f0 a   u f1 a   u f2  a  u f3 a

Where:
- :code:`u` = unnamed bits (unused)
- :code:`a` = added bits
- :code:`f0`, :code:`f1`, :code:`f2`, :code:`f3` = corresponding fields (`ancillary`, `private`, `reserved`, `safe_to_copy`)

Each bit or group of bits is allocated to a specific field, allowing you to
pack multiple flags or small values into a single byte or a group of bytes.


