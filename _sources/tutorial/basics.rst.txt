.. _basics:

**************
Basic Concepts
**************

In this section, we'll explore some common techniques used in binary file formats, setting
the stage for more advanced topics in the next chapter.

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


Strings
^^^^^^^

String handling is integral to binary formats, and Caterpillar introduces various utility strings
to facilitate this.

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

.. admonition:: Exercise

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

>>> field = CString(pad="\x0A")

This struct will use a space as the termination character and strip all trailing
padding bytes.








