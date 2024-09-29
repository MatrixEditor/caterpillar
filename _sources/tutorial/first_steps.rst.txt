.. _first-steps:

.. role:: python(code)
   :language: python

***********
First Steps
***********

In this section, we present examples designed to provide a relaxed introduction to *caterpillar*,
avoiding getting into technical details yet. Most of the code snippets are using interpreter
prompts. To reproduce the examples, simply input everything *after* the prompt.

In the context of this tutorial, we focus on the implementation of the `PNG <https://www.w3.org/TR/png/>`_
file format. While we won't list every available chunk, you're encouraged to explore and implement
additional chunks independently.

The PNG format organizes data into chunks, each following a common format. The global chunk
definition will be introduced later due to the impossibility of forward declarations in Python. [*]_

.. [*] It's technically possible to define the :ref:`pngchunk <switch-tutorial>` class here, but let's save that for later.

.. important::
    Assume that each code block starts with an import of all fields and the struct function from
    :code:`caterpillar.model`.

Defining structs
----------------

Given the important role of structs in this library, let's start by understanding their definition. Our
starting point is the `PLTE <https://www.w3.org/TR/png/#11PLTE>`_ chunk, which uses three-byte entries
for its data.

.. tab-set::

    .. tab-item:: Python

        .. code-block:: python
            :caption: RGB struct for the PLTE chunk

            from caterpillar.py import * # <-- just import everything

            @struct         # <-- just decorate the class with the struct() function
            class RGB:
                r: uint8    # <-- a field can be defined just like this
                g: uint8
                b: uint8


    .. tab-item:: Caterpillar C

        .. code-block:: python
            :caption: RGB struct for the PLTE chunk (using Caterpillar C)

            from caterpillar.c import * # <-- just import everything

            @struct         # <-- just decorate the class with the struct() function
            class RGB:
                r: u8       # <-- a field can be defined just like this
                g: u8
                b: u8

With this simple annotation, the struct class becomes universally applicable. You can
integrate it into other struct definitions or instantiate objects of the class.

>>> obj = RGB(1, 2, 3)

.. note::
    To optimize memory space and get faster attribute access times, you have to explicitly
    enable the :attr:`~caterpillar.options.S_SLOTS` option. More information can be taken from
    :ref:`options`.

Wow, thats it? That was less than expected? Let's move directly to working with the defined class.

Working with structs
--------------------

Instantiating an object of your class involves providing all **required** fields as arguments. They must be
keyword arguments if one of the defined fields contains a default value. Defaults or constant values are
automatically applied, removing concerns about them.

Packing data
^^^^^^^^^^^^

This library's packing and unpacking is similar to Python's `struct <https://docs.python.org/3/library/struct.html>`_
module. When packing data, a struct and an input object are needed.

Thanks to the RGB class encapsulating its struct instance, explicitly stating the struct to use
becomes unnecessary.

.. tab-set::

    .. tab-item:: Python

        >>> obj = RGB(r=1, g=2, b=3)
        >>> pack(obj) # equivalent to pack(obj, RGB)
        b'\x01\x02\x03'

    .. tab-item:: Caterpillar C

        >>> obj = RGB(r=1, g=2, b=3)
        >>> pack(obj, RGB) # required as of version 2.2.0
        b'\x01\x02\x03'


Unpacking data
^^^^^^^^^^^^^^

Recreating data from binary streams is as easy as serializing objects. Here, providing the struct directly
or our struct class is necessary.

.. tab-set::

    .. tab-item:: Python

        >>> unpack(RGB, b"\x01\x02\x03")
        RGB(r=1, g=2, b=3)

    .. tab-item:: Caterpillar C

        >>> unpack(b"\x01\x02\x03", RGB)
        RGB(r=1, g=2, b=3)


And no, we're not done yet - we've just wrapped up the warm-up!

Configuring structs
-------------------

Now, let's take a look at another chunk from the PNG format: `pHYS <https://www.w3.org/TR/png/#11pHYs>`_. It
specifies two four-byte unsigned integers. Given that PNG files encode numbers in *big-endian*, we must
configure the struct to correctly decode these integer fields.

.. admonition:: What is *endianess*?

    You might find these resources helpful: `Mozilla Docs <https://developer.mozilla.org/en-US/docs/Glossary/Endianness>`_,
    `StackOverflow <https://stackoverflow.com/questions/21449/types-of-endianness>`_ or
    `Wikipedia <https://en.wikipedia.org/wiki/Endianness>`_


.. tab-set::

    .. tab-item:: Python

        .. code-block:: python
            :caption: Configuring a struct-wide endianess

            @struct(order=BigEndian)        # <-- extra argument to apply the order to all fields.
            class PHYSChunk:
                pixels_per_unit_x: uint32   # <-- same definition as above
                pixels_per_unit_y: uint32
                unit: uint8                 # <-- endianess meaningless, only one byte

    .. tab-item:: Caterpillar C

        .. code-block:: python
            :caption: Configuring a struct-wide endianess

            @struct(endian=BIG_ENDIAN)   # <-- extra argument to apply the order to all fields.
            class PHYSChunk:
                pixels_per_unit_x: u32   # <-- same definition as above
                pixels_per_unit_y: u32
                unit: u8                 # <-- endianess meaningless, only one byte

        .. note::
            Even though, there will be :code:`<le uint32>` visible in the annotations
            of the class, the created struct stores the modified big endian integer
            atom.


If your structs depend on the architecture associated with the binary, you can also specify a
struct-wide :class:`~caterpillar.byteorder.Arch`.

.. admonition:: Challenge

    You can try to implement the struct for the `tIME <https://www.w3.org/TR/png/#11tIME>`_ chunk
    as a challenge.

    .. dropdown:: Solution
        :icon: check

        Example implementation

        .. tab-set::

            .. tab-item:: Python

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

            .. tab-item:: Caterpillar C

                .. code-block:: python
                    :linenos:

                    @struct(endian=BIG_ENDIAN)
                    class TIMEChunk:
                        year: u16        # <-- we could also use: BIG_ENDIAN + u16
                        month: u8
                        day: u8
                        hour: u8
                        minute: u8
                        second: u8

    Note that we can integrate this struct later on.


Documenting structs
^^^^^^^^^^^^^^^^^^^

To minimize changes to your codebase or require as little adaptation as possible from users of
this library, there's a documentation feature. By utilizing the ability to globally apply
options, you just need the following code:

.. tab-set::

    .. tab-item:: Python

        .. code-block:: python
            :caption: Enable documentation feature

            from caterpillar.shortcuts import opt

            opt.set_struct_flags(opt.S_REPLACE_TYPES)


    .. tab-item:: Caterpillar C

        .. code-block:: python
            :caption: Enable documentation feature

            from caterpillar.c import *

            STRUCT_OPTIONS.add(S_REPLACE_TYPES)

.. tip::
    If you are working with `Sphinx <https://www.sphinx-doc.org/en/master/>`_, you might need
    to enable :python:`autodoc_member_order = 'bysource'` to display all struct members in the
    correct order.

Next Steps
----------

With the fundamentals of defining and using structs, we're ready to start more advanced topics. The
upcoming sections will explore basic structs, array definitions, enum inclusion, and much more.