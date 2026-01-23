.. _first-steps:

***********
First Steps
***********

In this section, we provide an introduction to *Caterpillar*, avoiding the deeper technical
details for now. The goal is to offer a hands-on approach to get started. Most of the code
snippets are designed to be run in an interpreter, where you'll input everything **after**
the prompt to reproduce the examples.

To make the learning process more accessible, we'll focus on implementing the `PNG` file format,
as specified in the `PNG <https://www.w3.org/TR/png/>`_. While we won't cover every chunk type
in the format, we encourage you to explore and implement additional chunks on your own as you
progress through this tutorial.

**Why PNG?**

The PNG format organizes its data into distinct blocks known as **chunks**. Each chunk follows
a standard structure with specific fields and data, and *Caterpillar* allows you to map these
fields to Python classes effortlessly.

Since chunks are central to the PNG format, we'll focus on how to define and work with them.
However, it's important to note that the overall chunk definition will be introduced later.
Python's lack of support for forward declarations makes it a bit tricky to introduce the global
chunk definition upfront.

.. note::
    It's technically possible to define the `PNGChunk` class here (see :ref:`pngchunk <switch-tutorial>`), but we'll defer this for now to avoid overcomplicating things.

Before diving into the examples, keep in mind that each code snippet assumes you've already
imported the necessary components from *Caterpillar*:

>>> from caterpillar.py import *

.. tip::
    If you are working with caterpillar `>=2.8.0`, you can also import the default types for
    extended syntax:

    >>> from caterpillar.types import *


.. toctree::
    :caption: First Steps

    structdef
    parsing
    configuration
    documentation


Next Steps
----------

With the basics of defining, using, and documenting structs covered, we're
ready to dive deeper into more advanced topics. The
upcoming sections will explore basic structs, array definitions, enum inclusion, and much more.
