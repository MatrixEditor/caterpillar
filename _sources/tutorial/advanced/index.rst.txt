.. _advanced-concepts:

*****************
Advanced Concepts
*****************


Now that you've gained a basic understanding of how the library works, we can dive
deeper into more advanced concepts. This section will help you master the usage of
specialized features, and by the end of this tutorial, you'll be well-equipped to
create and manipulate your own custom struct classes in Python.

.. toctree::
    :caption: Advanced Topics for Catepillar (Python)
    :maxdepth: 2

    operators
    byteorder
    pointers
    chaining
    conditional
    actions
    bitfield
    union
    templates


.. rubric:: The End!

We finish this tutorial by completing our PNG format implementation. As the format is just
a collection of chunks, we can simply alter the *main* struct from before:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :caption: Final PNG implementation

            @struct
            class PNG:
                magic: b"\x89PNG\x0D\x0A\x1A\x0A"
                # We don't know the length, therefore we need greedy parsing
                chunks: PNGChunk[...]

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :caption: Final PNG implementation

            @struct
            class PNG:
                magic: f[bytes, b"\x89PNG\x0D\x0A\x1A\x0A"]
                # We don't know the length, therefore we need greedy parsing
                chunks: f[list[PNGChunk], PNGChunk[...]]


**Thats it!** We now have a qualified PNG image parser **and** builder just using some
Python class definitions.

.. code-block:: python
    :caption: Sample usage of the PNG struct

    >>> image = unpack_file(PNG, "/path/to/image.png")
    >>> image
    PNG(magic=b'\x89PNG\r\n\x1a\n', chunks=[PNGChunk(length=13,type='IHDR', body=..., crc=258163462), ...])
    >>> pack_file(image, "/path/to/destination")


*This is the end of our journy to the basics of caterpillar. Below is a collection of useful
resources that might help you progress any further.*

.. seealso::
    * :ref:`reference-index`
    * :ref:`library-index` API Docs
    * `Github Source <https://github.com/MatrixEditor/caterpillar>`_
    * `Implemented Formats <https://github.com/MatrixEditor/caterpillar/tree/master/examples/formats>`_

