.. _tutorial-basic_other:

=================
Common Structures
=================

In addition to the basic field types we've already covered, *Caterpillar* offers more
advanced struct types for handling complex data structures. These types can simplify
parsing and packing operations, especially when dealing with constants, compression,
or specialized data handling.

Constants
---------

In many binary formats, constants or "magic bytes" are used to identify the start
of a file or data stream. *Caterpillar* allows you to define and automatically
validate these constants against the parsed data, saving you from manually adding
them in every time.

For instance, a PNG file starts with a known sequence of magic bytes:
:code:`\\x89PNG\\x0D\\x0A\\x1A\\x0A`. You can define these constants directly in your
struct like so:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :caption: Starting the *main* PNG struct

            @struct(order=BigEndian) # <-- will be relevant later on
            class PNG:
                magic: b"\x89PNG\x0D\x0A\x1A\x0A"
                # other fields will be defined at the end of this tutorial.


    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :caption: Starting the *main* PNG struct

            @struct(order=BigEndian) # <-- will be relevant later on
            class PNG:
                magic: f[bytes, b"\x89PNG\x0D\x0A\x1A\x0A"] = Invisible()
                # other fields will be defined at the end of this tutorial.


For raw constant values, *Caterpillar* provides the :class:`~caterpillar.py.Const`
struct, which allows you to define constant values that need to be packed or
unpacked.

>>> const = Const(0xbeef, uint32)

Compression
-----------

*Caterpillar* also supports common compression formats such as `zlib`, `lzma`, `bz2`,
and, if the library is installed, `lzo`. This allows you to handle compressed data
within your struct definitions easily.

>>> compressed = ZLibCompressed(100) # length or struct here applicable

Specials
--------

There are several special structs for handling more advanced or less common scenarios.

Computed
~~~~~~~~

The `Computed` struct allows you to define a runtime computed variable that doesn't
actually pack any data. While you could use a :code:`@property` or method to represent
this, :code:`Computed` is useful when you need to calculate a value during the packing
or unpacking process.

You might want to compute the real gamma value for a PNG chunk, based on another field
in the struct:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :caption: Example implementation of the *gAMA* chunk

            @struct(order=BigEndian)    # <-- same as usual
            class GAMAChunk:
                gamma: uint32
                gamma_value: Computed(this.gamma / 100000)

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :caption: Example implementation of the *gAMA* chunk

            @struct(order=BigEndian)    # <-- same as usual
            class GAMAChunk:
                gamma: uint32_t
                gamma_value: f[float, Computed(this.gamma / 100000)] = 0.0

Pass
~~~~

The :code:`Pass` struct is used when no action should be taken during the packing or unpacking
process. It doesn't affect the data stream in any way.

You can use `Pass` when you simply need to skip over certain parts of the data without modifying them:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        >>> @struct
        ... class Format:
        ...     foo: Pass  # This won't affect the stream and will store None
        ...

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        >>> @struct
        ... class Format:
        ...     foo: pass_t = None  # This won't affect the stream and will store None
        ...