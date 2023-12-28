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

Comparison
----------

*TODO: add links*

Here, we present a comparison of Caterpillar with Construct and Kaitai using the struct
from the initial benchmark in the `construct-docs`_ repository as a base.Since Kaitai's
generated code can only parse a format and not build it, the comparison is focused on
Construct. The files used in the benchmark are provided below:

.. tab-set::

    .. tab-item:: caterpillar

        .. literalinclude:: ./snippets/comparison_1_caterpillar.py
            :language: python

        .. note::
            It actually makes no time-related difference if we define the :code:`Format` field directly or put it into
            a struct class.

    .. tab-item:: construct

        .. literalinclude:: ./snippets/comparison_1_construct.py
            :language: python

    .. tab-item:: kaitai

        .. literalinclude:: ./snippets/comparison_kaitai.ksy
            :language: yaml

    .. tab-item:: hachoir

        .. literalinclude:: ./snippets/comparison_1_hachoir.py
                :language: python

    .. tab-item:: mrcrwobar

        .. literalinclude:: ./snippets/comparison_1_mrcrowbar.py
                :language: python


The test involved one thousand iterations of packing and unpacking the structure. Kaitai
scores with the fastest time since it directly reads all data from the stream. *caterpillar*
and Construct show similar performance in their initial form. The compilation feature of
Construct makes it comparable to Kaitai, but since compilation is not a primary goal of
*caterpillar*, these results are not considered.

.. tab-set::

    .. tab-item:: caterpillar

        .. code-block:: console
            :caption: caterpillar

            (venv-3.12.1)> python3 ./examples/comparison/comparison_1_caterpillar.py ./blob
            Timeit measurements:
            unpack 0.0115265591 sec/call        # +- 0.0004 sec
            pack   0.0104318993 sec/call        # +- 0.0002 sec

    .. tab-item:: construct

       .. code-block:: console
            :caption: Construct

            (venv-3.12.1)> python3 ./examples/comparison/comparison_1_construct.py ./blob
            Parsing measurements:
            default  0.0143656098 sec/call
            compiled 0.0085707553 sec/call

            Building measurements:
            default  0.0127780359 sec/call
            compiled 0.0099577958 sec/call

    .. tab-item:: kaitai

        .. code-block:: console
            :caption: kaitai

            (venv-3.12.1)> python3 ./examples/comparison/comparison_1_kaitai.py ./blob
            Parsing measurements:
            default  0.0034705456 sec/call

    .. tab-item:: hachoir

        .. code-block:: console
            :caption: hachoir

            (venv-3.12.1)> python3 ./examples/comparison/comparison_1_hachoir.py ./blob
            Parsing measurements:
            default  0.0260070809 sec/call

    .. tab-item:: mrcrwobar

        .. code-block:: console
            :caption: mrcrwobar

            (venv-3.12.1)> python3 ./examples/comparison/comparison_1_mrcrowbar.py ./blob
            Parsing measurements:
            default  0.0555872261 sec/call

            Building measurements:
            default  0.0898006975 sec/call

In this benchmark, *caterpillar* demonstrates a performance advantage, being approximately :bdg-success:`19.76%`
faster in unpacking data and approximately :bdg-success:`18.36%` faster in packing data compared to Construct
(*not compiled*).

In the **compiled** Construct test, *caterpillar* shows a performance difference compared to Construct. Specifically,
*caterpillar* is approximately :bdg-danger:`34.48%` slower in unpacking data and approximately
:bdg-warning:`4.76%` slower in packing data. It's important to note that these figures reflect a trade-off between
performance and other considerations such as simplicity and ease of use.


.. |c0| unicode:: U+02C8
.. |c1| unicode:: U+00E6
.. |c2| unicode:: U+0259
.. |c3| unicode:: U+026A
.. |c4| unicode:: U+0259

.. [1] https://en.wikipedia.org/wiki/Caterpillar
.. [2] Even structs generated from class models are extensible in some degree.


.. _construct-docs: https://construct.readthedocs.io/en/latest/compilation.html#comparison-with-kaitai-struct