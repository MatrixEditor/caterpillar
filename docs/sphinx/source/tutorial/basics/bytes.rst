.. _tutorial-basics-bytes:

**************
Byte Sequences
**************

When working with binary data, sometimes you need to deal with raw byte
sequences. *Caterpillar* provides several structs to handle these byte
sequences efficiently, whether they are stored in memory, byte arrays,
or prefixed with length information.

Memory
~~~~~~

The :class:`~caterpillar.py.Memory` struct is ideal when you need to handle
data that can be wrapped by a :code:`memoryview`. It allows you to define
fields with a specified size (static or dynamic) and is especially useful
for printing out unpacked objects in a readable way.


>>> m = Memory(5) # static size; dynamic size is allowed too
>>> pack(bytes([i for i in range(5)], m))
b'\x00\x01\x02\x03\x04'
>>> unpack(m, _)
<memory at 0x00000204FDFA4411>

Bytes
~~~~~

If you need direct access to byte sequences, the :class:`~caterpillar.py.Bytes`
struct is the solution. This struct converts a :code:`memoryview` to :code:`bytes`
for easy manipulation. You can define fields with static, dynamic, or greedy
sizes based on your needs.

>>> bytes_obj = Bytes(5) # static, dynamic and greedy size allowed


Let's implement a struct for the `fDAT <https://www.w3.org/TR/png/#fdAT-chunk>`_ chunk
of the PNG format, which stores frame data. In this case, we use the :code:`Memory`
struct to handle the frame data.

.. code-block:: python
    :caption: Implementation for the frame data chunk

    @struct(order=BigEndian)                    # <-- endianess as usual
    class FDATChunk:
        sequence_number: uint32
        # We rather use a memory instance here instead of Bytes()
        frame_data: Memory(parent.length - 4)


.. admonition:: Challenge

    If you feel ready for a more advanced structure, try implementing the
    `zTXt <https://www.w3.org/TR/png/#11zTXt>`_ chunk for compressed textual data.

    .. dropdown:: Solution

        .. code-block:: python
            :caption: Sample implementation of the *zTXt* chunk

            @struct                             # <-- actually, we don't need a specific byteorder
            class ZTXTChunk:
                keyword: CString(...)           # <-- variable length
                compression_method: uint8
                # Okay, we haven't introduced this struct yet, but Memory() or Bytes()
                # would heve been okay, too.
                text: ZLibCompressed(parent.length - lenof(this.keyword) - 1)
