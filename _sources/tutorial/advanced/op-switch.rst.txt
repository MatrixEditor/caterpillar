.. _switch-tutorial:

Switch
******

A key feature that *caterpillar* provides out of the box is support for switch-case
structures. This feature allows you to model conditional data processing in a clean,
efficient way without the need for a custom implementation.

While there are some limitations to the usage of certain operators, their basic
functionality should be more than sufficient for most use cases. To illustrate this,
let's revisit the PNG format implementation and define a common chunk type using a
switch-case structure.


.. tab-set::
   :sync-group: syntax

   .. tab-item:: Default Syntax
      :sync: default

      .. code-block:: python
         :caption: Implementation of the general `chunk layout <https://www.w3.org/TR/png/#5Chunk-layout>`_

         @struct(order=BigEndian)
         class PNGChunk:
            length: uint32          # length of the data field (1)
            type: Bytes(4)
            data: F(this.type) >> { # just use right shift (2)
                  b"IHDR": IHDRChunk,
                  b"PLTE": PLTEChunk, # the key must be comparable to this.type
                  b"pHYs": PHYSChunk,
                  b"iTXt": ITXTChunk,
                  b"tIME": TIMEChunk,
                  b"tEXt": TEXTChunk,
                  b"iTXt": ITXTChunk,
                  b"fDAT": FDATChunk,
                  b"zTXt": ZTXTChunk,
                  b"gAMA": GAMAChunk,
                  # Special case: IEND chunk, which doesn’t need to parse any data
                  b"IEND": Pass # (4)
                  # As we don't define all chunks here for now, a default
                  # option must be provided
                  DEFAULT_OPTION: Memory(this.length) # (3)
            }

   .. tab-item:: Extended Syntax (>=2.8.0)
      :sync: extended

      .. code-block:: python
         :caption: Implementation of the general `chunk layout`

         # just for your type checker:
         ChunkT = (
            IHDRChunk
            | PLTEChunk
            | PHYSChunk
            | ITXTChunk
            | TIMEChunk
            | TEXTChunk
            | ITXTChunk
            | FDATChunk
            | ZTXTChunk
            | GAMAChunk
            | None # pass (4)
            | memoryview # all unknown chnks
         )

         @struct(order=BigEndian)
         class PNGChunk:
            length: uint32_t          # length of the data field (1)
            type: f[bytes, Bytes(4)]
            data: f[ChunkT,
               F(this.type) >> { # just use right shift (2)
                  b"IHDR": IHDRChunk,
                  b"PLTE": PLTEChunk, # the key must be comparable to this.type
                  b"pHYs": PHYSChunk,
                  b"iTXt": ITXTChunk,
                  b"tIME": TIMEChunk,
                  b"tEXt": TEXTChunk,
                  b"iTXt": ITXTChunk,
                  b"fDAT": FDATChunk,
                  b"zTXt": ZTXTChunk,
                  b"gAMA": GAMAChunk,
                  # Special case: IEND chunk, which doesn’t need to parse any data
                  b"IEND": Pass # (4)
                  # As we don't define all chunks here for now, a default
                  # option must be provided
                  DEFAULT_OPTION: Memory(this.length) # (3)
               }
            ]


1. **Length and Type**:
   The `PNGChunk` struct has two main fields: `length` (the length of the data field) and `type`
   (the 4-byte identifier of the chunk type). These fields are standard across all PNG chunks.

2. **Dynamic Chunk Handling (Switch-Case)**:
   The `data` field uses a dynamic mapping of chunk types to specific chunk structs. We use the :code:`>>`
   operator (right shift) to define this mapping, where each chunk type corresponds to a specific
   struct (e.g., `IHDRChunk`, `PLTEChunk`, etc.).

3. **Default Option**:
   For chunk types that are not explicitly defined in the mapping, we provide a default option.
   In this case, `DEFAULT_OPTION` stores the raw chunk data as a `Memory` object, which is useful
   for handling unrecognized or unknown chunk types.

4. **Special Handling for `IEND`**:
   The `IEND` chunk, which marks the end of a PNG file, does not require any data parsing. We simply
   map it to `Pass`, a special directive indicating that no further processing is needed for this chunk.
