.. _basics:

**************
Basic Concepts
**************

In this section, we'll explore some common techniques used in binary file formats, setting
the stage for more advanced topics in the next chapter.

.. attention::
    Some examples using the interpreter prompts make use of a shortcut to define :class:`Field`
    objects:

    >>> from caterpillar.shortcuts import F
    >>> field = F(uint8)

Standard Types
--------------

Enumerations
^^^^^^^^^^^^

Enums are essential when working with binary file formats, and *caterpillar* integrates
standard Python enumerations - classes extending  :code:`enum.Enum` - with ease.

Let's revisit `pHYS <https://www.w3.org/TR/png/#11pHYs>`_ chunk to add an enum to the
last field.

.. code-block:: python
    :caption: Simple enumeration in a struct definition

    import enum

    class PHYSUnit(enum.IntEnum): # <-- the enum value doesn't have to be int
        UNKNOWN = 0
        METRE = 1

    @struct(order=BigEndian)         # <-- same as before
    class PHYSChunk:
        pixels_per_unit_x: uint32
        pixels_per_unit_y: uint32
        unit: Enum(PHYSUnit, uint8)  # <-- now we have an auto-enumeration

.. important::
    It's worth noting that a default value can be specified for the field as a fallback. If
    none is provided, and an unpacked value not in the enumeration is encountered, an error
    will be triggered.


Arrays/Lists
^^^^^^^^^^^^

Binary formats often require storing multiple objects of the same type sequentially. *Caterpillar*
simplifies this with item access for defining arrays of static or dynamic size.

We started with the `PLTE <https://www.w3.org/TR/png/#11PLTE>`_ chunk, which stores three-byte
sequences. We can define an array of RGB objects as follows:

>>> PLTEChunk = RGB[this.length / 3]

Since this chunk has only one field, the array specifier is used to make it a list type. The
length is calculated based on the chunk's length field divided by three because the RGB class
occupies three bytes.


String Types
^^^^^^^^^^^^

CString
~~~~~~~

The CString in this library extends beyond a mere reference to C strings. It provides
additional functionality, as demonstrated in the structure of the next chunk.

.. code-block:: python
    :caption: The `tEXt <https://www.w3.org/TR/png/#11tEXt>`_ chunk structure

    @struct
    class TEXTChunk:
        # dynamic sized string that ends with a null-byte
        keyword: CString(encoding="ISO-8859-1")
        # static sized string based on the current context. some notes:
        #   - parent.length is the current chunkt's length
        #   - lenof(...) is the runtime length of the context variable
        #   - 1 because of the extra null-byte that is stripped from keyword
        text: CString(encoding="ISO-8859-1", length=parent.length - lenof(this.keword) - 1)

.. admonition:: Challenge

    You are now ready to implement the `iTXt <https://www.w3.org/TR/png/#11iTXt>`_ chunk. Try it yourself!

    .. dropdown:: Solution
        :icon: check

        This solution serves as an example and isn't the only way to approach it!

        .. code-block:: python

            @struct
            class ITXTChunk:
                keyword: CString(encoding="utf-8")
                compression_flag: uint8
                # we actually don't need an Enum here
                compression_method: uint8
                language_tag: CString(encoding="ASCII")
                translated_keyword: CString(encoding="utf-8")
                # length is calculated with parent.length - len(keyword)+len(b"\x00") - ...
                text: CString(
                    encoding="utf-8",
                    length=parent.length - lenof(this.translated_keyword) - lenof(this.keyword) - 5,
                )

You can also apply your own termination character, for example:

>>> struct = CString(pad="\x0A")

This struct will use a space as the termination character and strip all trailing
padding bytes.

String
~~~~~~

Besides special the special *c strings* there's a default :class:`String` class that implements
the basic behaviour of a string. It's crucial to specify the length for this struct.

>>> struct = String(100 or this.length) # static integer or context lambda


Prefixed
~~~~~~~~

The :class:`Prefixed` class introduces so-called *Pascal strings* for raw bytes and strings. If no
encoding is specified, the returned value will be of type :code:`bytes`. This class reads a length
using the given struct and then retrieves the corresponding number of bytes from the stream returned
by that struct.

>>> field = F(Prefixed(uint8, encoding="utf-8"))
>>> pack("Hello, World!", field)
b'\rHello, World!'
>>> unpack(field, _)
'Hello, World!'


Byte Sequences
^^^^^^^^^^^^^^

Memory
~~~~~~

When dealing with data that can be stored in memory and you intend to print out your
unpacked object, the :class:`Memory` struct is recommended.

>>> m = F(Memory(5)) # static size, dynamix size is allowed too
>>> pack(bytes([i for i in range(5)], m))
b'\x00\x01\x02\x03\x04'
>>> unpack(m, _)
<memory at 0x00000204FDFA4411>

Bytes
~~~~~

If direct access to the bytes is what you need, the :class:`Bytes` struct comes in handy. It
converts the :code:`memoryview` to :code:`bytes`. Additionally, as mentioned earlier, you can
use the :class:`Prefixed` class to unpack bytes of a prefixed size.




