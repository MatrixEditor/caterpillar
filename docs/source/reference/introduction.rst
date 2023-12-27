.. _introduction:

************
Introduction
************

The "library reference" contains several different documents describing the core model of this framework. After
the tutorial, you are now able to dive deeper into the functionalities of this library.

.. admonition:: What exactly is a *caterpillar*?

    Caterpillars (|c0|/k |c1| t |c2| rp |c3| l |c4| r - 🐛) are the wormlike larva of a butterfly or moth. [1]_
    Just as caterpillars undergo a metamorphosis, *caterpillar* facilitates the metamorphosis of data structures
    into runtime objects.


This document aims to address burning questions regarding design and availability. It provides an overview of the
aspects covered by this framework and those that it doesn't. In general, this library was designed to enhance the
process of reverse engineering binary structures using readable and shareable code. The use of *"static"* [2]_
class definitions delivers advantages but also brings up some problems that we need to discuss.


Why use Caterpillar?
--------------------

There are several reasons to incorporate this library into your code. Some of the scenarios where Caterpillar can
be beneficial including

- **Quick Reverse Engineering**: When you need to rapidly reverse engineer a binary structure.
- **Creating Presentable Binary Structures**: When there's a task to create a binary structure, and the result should be presentable.
- **Have some fun**: or when you just want to experiment and play around in Python.


The biggest advantage of *Caterpillar* is the lack of external dependencies (though extensions can be integrated using
dependencies). Additionally, the minimal lines of code required to define structures speak for themselves, as
demonstrated in the following example from `examples/formats/caf`:

.. code-block:: python
    :linenos:

    @struct(order=BigEndian)
    class CAFChunk:
        # Include other structs just like that
        chunk_header: CAFChunkHeader
        # Built-in support for switch-case structures
        data: Field(this.chunk_header.chunk_type) >> {
            b"desc": CAFAudioFormat,
            b"info": CAFStringsChunk,
            b"pakt": CAFPacketTable,
            b"data": CAFData,
            b"free": padding[this.chunk_header.chunk_size],
            # the fallback struct given with a default option
            DEFAULT_OPTION: Bytes(this.chunk_header.chunk_size),
        }


How does this even work?
^^^^^^^^^^^^^^^^^^^^^^^^

*Caterpillar* utilizes Python's annotations to build its model from processing class definitions. With the use
of Python 3.12, there are no conflicts in using annotations for defining fields.

.. code-block:: python

    @struct
    class Format:
        # <name> : <field> [ = <default_value> ]

By using annotations, we can simply define a default value if desired, eliminating the need to make the code
more complex by using assignments.

Pros & Cons
-----------

*TODO*




.. |c0| unicode:: U+02C8
.. |c1| unicode:: U+00E6
.. |c2| unicode:: U+0259
.. |c3| unicode:: U+026A
.. |c4| unicode:: U+0259

.. [1] https://en.wikipedia.org/wiki/Caterpillar
.. [2] Even structs generated from class models are extensible in some degree.