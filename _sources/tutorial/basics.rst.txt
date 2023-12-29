.. _basics:

**************
Basic Concepts
**************

In this section, we'll explore some common techniques used in binary file formats, setting
the stage for more advanced topics in the next chapter.

.. note::
    Some examples using the interpreter prompts make use of a shortcut to define :class:`Field`
    objects:

    >>> from caterpillar.shortcuts import F
    >>> field = F(uint8)

Standard Types
--------------

Numbers
^^^^^^^

When dealing with binary data, numbers play a crucial role. Besides the default integer types
(e.g., uint8, uint16, etc.), *caterpillar* introduces some special integer formats. The default
types include:

* Unsigned (:code:`u...`) and signed: :attr:`int8`, :attr:`int16`, :attr:`int32` and :attr:`int64`
* Floating point: :attr:`float32` and :attr:`float64` aka :attr:`double`

Custom-sized integer
~~~~~~~~~~~~~~~~~~~~

It's also possible to use integers with a custom size (in bits). However, it's important to note
that you have to define the struct with the bit count, and internally, only the occupied bytes
will be used. For example:

>>> field = F(Int(24))      # three-byte signed integer

>>> field = F(UInt(40))     # five-byte unsigned integer


Variable-sized integer
~~~~~~~~~~~~~~~~~~~~~~

The built-in struct :class:`VarInt` supports parsing and building integers with variable length. Its
documentation provides a detailed explanation of all different configurations.

>>> field = F(VarInt)


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

>>> m = F(Memory(5)) # static size; dynamic size is allowed too
>>> pack(bytes([i for i in range(5)], m))
b'\x00\x01\x02\x03\x04'
>>> unpack(m, _)
<memory at 0x00000204FDFA4411>

Bytes
~~~~~

If direct access to the bytes is what you need, the :class:`Bytes` struct comes in handy. It
converts the :code:`memoryview` to :code:`bytes`. Additionally, as mentioned earlier, you can
use the :class:`Prefixed` class to unpack bytes of a prefixed size.

>>> field = F(Bytes(5)) # static, dynamic and greedy size allowed


With the gained knowledge, let's implement the struct for the `fDAT <https://www.w3.org/TR/png/#fdAT-chunk>`_
chunk of our PNG format. It should look like this:

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


Padding
^^^^^^^

In certain scenarios, you may need to apply padding to your structs. *caterpillar* doesn't
store any data associated with paddings. If you need to retain the content of a padding,
you can use :class:`Bytes` or :class:`Memory` again. For example:

>>> field = padding[10]  # padding always with a length


.. tip::
    That was a lot of input to take, time for a coffee break! |coffee|


Context
-------

*Caterpillar* uses a special :class:`Context` to keep track of the current packing or unpacking
process. A context contains special variables, which are discussed in the :ref:`context-reference`
reference in detail.

The current object that is being packed or parsed can be referenced with a shortcut :code:`this`.
Additionally, the parent object (if any) can be referenced by using :code:`parent`.


.. code-block:: python
    :caption: Understanding the *context*

    @struct
    class Format:
        length: uint8
        foo: CString(this.length)   # <-- just reference the length field

.. note::
    You can apply any operation on context paths. However, be aware that conditional branches must
    be encapsulated by lambda expressions.

Runtime length of objects
^^^^^^^^^^^^^^^^^^^^^^^^^

In cases where you want to retrieve the runtime length of a variable that is within the current
accessible bounds, there is a special class designed for that use-case: :attr:`lenof`.

You might have seen this special class before when calculating the length of some strings. It
simply applies the :python:`len(...)` function of the retrieved variable.

.. tip::
    To access elements of a sequence within the context, you can just use :python:`this.foobar[...]`.


Standard Structs
----------------

We still have some important struct types to discuss to start defining *complex* structs.

Constants
^^^^^^^^^

Proprietary file formats or binary formats often store `magic bytes <https://www.garykessler.net/library/file_sigs.html>`_
usually at the start of the data stream. Constant values will be validated against the parsed
data and will be applied to the class automatically, eliminating the need to write them into
the constructor every time.

ConstBytes
~~~~~~~~~~

These constants can be defined implicitly by annotating a field in a struct class with bytes.
For example, in the case of starting the *main* PNG struct:

.. code-block:: python
    :caption: Starting the *main* PNG struct

    @struct(order=BigEndian) # <-- will be relevant later on
    class PNG:
        magic: b"\x89PNG\x0D\x0A\x1A\x0A"
        # other fields will be defined at the end of this tutorial.

Const
~~~~~

Raw constant values require a struct to be defined to parse or build the value.
For example:

>>> field = F(Const(0xbeef, uint32))


Compression
^^^^^^^^^^^

This library also supports default compression formats like *zlib*, *lzma*, *bz2* and, if
installed via pip, *lzo* (using :code:`lzallright`).

>>> field = ZLibCompressed(100) # length or struct here applicable

Specials
^^^^^^^^

All of the following structs may be used in special situations where all other previously
discussed structs can't be used.

Computed
~~~~~~~~

A runtime computed variable that does not pack any data. It is rarely recommended to use this
struct, because you can simply define a :code:`@property` or method for what this structs
represents, **unless** you need the value later on while packing or unpacking.

>>> struct = Computed(this.foobar) # context lambda or constant value

.. admonition:: Challenge

    Implement the `gAMA <https://www.w3.org/TR/png/#11gAMA>`_ chunk for our PNG format and use
    a :class:`Computed` struct to calculate the real gamma value.

    .. dropdown:: Solution

        .. code-block:: python
            :caption: Example implementation of the *gAMA* chunk

            @struct(order=BigEndian)    # <-- same as usual
            class GAMAChunk:
                gamma: uint32
                gamma_value: Computed(this.gamma / 100000)

        .. note::
            Question: Do we really need to introduce the gamma_value using a :class:`Computed` struct here
            or can we just define a method?

Pass
~~~~

In case nothing should be done, just use :class:`Pass`. This struct won't affect the stream in any way.

.. raw:: html

    <hr>

.. important::
    Congratulations! You have successfully mastered the basics of *caterpillar*! Are you
    ready for the next level? Brace yourself for some breathtaking action!

.. |coffee| unicode:: U+2615