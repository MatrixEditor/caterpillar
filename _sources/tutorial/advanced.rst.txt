.. _advanced-concepts:

*****************
Advanced Concepts
*****************

*TODO*

Now that you've acquired a general understanding of how this library works, let's
start the more advanced concepts. This document will bring the tutorial to a close,
leaving you well-equipped to create your own struct classes in Python.

.. attention::
    Most of the structs and techniques showcased here are subject to change, notably
    :class:`BitField` and :code:`@union`. Their current usage is not as user-friendly
    as expected.


Operators
---------

Switch
^^^^^^

*TODO*

Offset
^^^^^^

*TODO*

BitFields
---------

*TODO* description

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

    # byte     :     0        1       2        3
    # bit      : 76543210 76543210 76543210 76543210
    # ----------------------------------------------
    # breakdown: 00100000 00100000 00100000 00100000
    #            \/|\___/ \/|\___/ \/|\___/ \/|\___/
    #            u f0 a   u f1 a   u f2  a  u f3 a
    # Where u='unnamed', a='added' and 'f..'=corresponding fields


Unions
------

*TODO* description

.. code-block:: python
    :caption: Combining the name with its naming convention

    @union
    class ChunkName:
        text: Bytes(4)
        options: ChunkOptions


The End!
--------

*TODO: implement final PNG struct*

