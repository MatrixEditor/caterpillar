.. _tutorial-basics-stdtypes_enum:

************
Enumerations
************

When working with binary formats, enumerations (enums) are an important feature,
allowing you to define and use named constants for field values. In *Caterpillar*,
you can easily integrate standard Python enumerations, which are classes extending
:code:`enum.Enum`, into your struct definitions.

For example, in the case of the  `pHYS <https://www.w3.org/TR/png/#11pHYs>`_ chunk
from the PNG format, you can use an enum for the :code:`unit` field, which represents
the unit of measurement (like "meter"). Here's how you would define it:


.. code-block:: python
    :caption: Simple enumeration in a struct definition

    import enum

    class PHYSUnit(enum.IntEnum): # <-- the enum value doesn't have to be int
        __struct__ = uint8        # <-- to make the code even more compact, use this
        UNKNOWN = 0
        METRE = 1

    @struct(order=BigEndian)         # <-- same as before
    class PHYSChunk:
        pixels_per_unit_x: uint32
        pixels_per_unit_y: uint32
        unit: PHYSUnit               # <-- now we have an auto-enumeration



.. important::

    - You can specify a default value for the enum field, which will be used as a fallback if the unpacked data contains a value not in the enumeration.
    - If no default is provided and the unpacked data contains an unexpected value, an error will be raised.
