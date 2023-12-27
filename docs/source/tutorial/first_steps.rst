.. _first-steps:

***********
First Steps
***********

In this section, we present illustrative examples designed to provide a relaxed introduction to
*caterpillar*, avoiding getting into technical details. Most of the code snippets are interactive,
utilizing interpreter prompts. To reproduce the examples, simply input everything *after* the
prompt.

In the context of this tutorial, we focus on the implementation of the `PNG <https://www.w3.org/TR/png/>`_
format. While we won't delve into every available chunk, you're encouraged to explore and implement
additional chunks independently.

The PNG format organizes data into chunks, each following a common format. The global chunk
definition will be introduced later due to the impossibility of forward declarations in Python. [*]_

.. [*] While it's technically possible to define the :ref:`pngchunk` class here, let's save that for later.

Defining structs
----------------

Given the important role of structs in this library, let's start by understanding their definition. Our
starting point is the `PLTE <https://www.w3.org/TR/png/#11PLTE>`_ chunk, which uses three-byte entries
for its data.

.. code-block:: python
    :caption: RGB struct for the PLTE chunk

    @struct         # <-- just decorate the class with the struct() function
    class RGB:
        r: uint8    # <-- a field can be defined just like this
        g: uint8
        b: uint8

With this simple annotation, the struct class becomes universally applicable. You can
integrate it into other struct definitions or instantiate objects of the class.

>>> obj = RGB(x=1, y=2, z=3)

.. note::
    Classes using the :code:`struct` decorator exclusively accept keywords in the final constructor,
    supporting standard field definitions *after* fields with default values.
