.. _first_steps-config:

Configuring structs
===================

When working with binary data, it's essential to account for how the data is ordered, particularly
when dealing with multi-byte fields. The **endianess** of the data specifies the byte order:
either **big-endian** (most significant byte first) or **little-endian** (least significant byte first).
In this section, we'll look at how to configure the endianess for structs in *Caterpillar*.

.. admonition:: What is *endianess*?

    You might find these resources helpful: `Mozilla Docs <https://developer.mozilla.org/en-US/docs/Glossary/Endianness>`_,
    `StackOverflow <https://stackoverflow.com/questions/21449/types-of-endianness>`_ or
    `Wikipedia <https://en.wikipedia.org/wiki/Endianness>`_


Let's take a look at another chunk from the PNG format: the `pHYS <https://www.w3.org/TR/png/#11pHYs>`_ chunk.
It contains two 4-byte unsigned integers that represent pixel density. Since PNG files use **big-endian** encoding
for integers, we need to configure the struct to handle this correctly.

.. code-block:: python
    :caption: Configuring a struct-wide endianess

    @struct(order=BigEndian)        # <-- extra argument to apply the order to all fields.
    class PHYSChunk:
        pixels_per_unit_x: uint32   # <-- same definition as above
        pixels_per_unit_y: uint32
        unit: uint8                 # <-- endianess meaningless, only one byte

In both cases, the :code:`pixels_per_unit_x` and :code:`pixels_per_unit_y` fields are 4 bytes long,
so they will be interpreted using big-endian encoding. The :code:`unit` field is only 1 byte, so
endianess doesn't affect it.

.. tip::
    It is also possible to mixup various byte orders within the same struct by applying the
    endianess directly to the field types. Additionally, there is a special byte order type
    that allows dynamic selection of the endian during runtime. See the
    :ref:`advanced configuration <tutorial-dyn_byteorder>` section for more details.

In addition to configuring the endianess, you can also specify the **architecture** associated
with the struct using the :class:`~caterpillar.byteorder.Arch` class with the :code:`arch` keyword.


.. admonition:: Challenge

    You can try to implement the struct for the `tIME <https://www.w3.org/TR/png/#11tIME>`_ chunk
    as a challenge.

    .. dropdown:: Solution
        :icon: check

        Example implementation

        .. code-block:: python
            :linenos:

            @struct(order=BigEndian)
            class TIMEChunk:
                year: uint16        # <-- we could also use: BigEndian + uint16
                month: uint8
                day: uint8
                hour: uint8
                minute: uint8
                second: uint8

        As you can see, the struct is fairly simple. The year field is 2 bytes, and the rest are
        single-byte fields. By applying :code:`BigEndian` or :code:`BIG_ENDIAN` to the struct,
        we ensure that the fields that require endian configuration are handled correctly.



