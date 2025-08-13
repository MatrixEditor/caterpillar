.. _first_steps-structdef:

Defining Structs
=================

Structs are at the heart of this library, and understanding how to define and use them
is key to leveraging the full power of *Caterpillar*. In this section, we'll begin by
defining a simple struct for the  `PLTE <https://www.w3.org/TR/png/#11PLTE>`_ chunk of
a PNG file, which consists of three-byte entries.

.. code-block:: python
    :caption: RGB struct for the PLTE chunk

    from caterpillar.py import * # <-- just import everything

    @struct         # <-- just decorate the class with the struct() function
    class RGB:
        r: uint8    # <-- a field can be defined just like this
        g: uint8
        b: uint8


By using the :code:`@struct` decorator, we've defined the :code:`RGB` class as
a struct. This simple annotation turns the class into a structured representation
of the data. Once defined, you can easily instantiate objects of the :code:`RGB`
class and assign values to its fields:

>>> obj = RGB(1, 2, 3)

At this point, the `RGB` class is ready to be used as part of larger struct definitions
or on its own.

.. tip::
    If you're working with large numbers of instances or require fast attribute access,
    you can optimize the memory usage and speed by enabling the :attr:`~caterpillar.options.S_SLOTS`
    option. This reduces the overhead of using dictionaries for attribute storage. For more details
    on how to enable this option, refer to the documentation on :ref:`options`.


Thats it? That was less than expected? Let's move directly to working with the defined class.
