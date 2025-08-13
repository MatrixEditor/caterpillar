.. _first_steps-parsing:

Working with Structs
====================

Once you've defined your struct, you can create instances of it by passing values
to the required fields. If any of the fields have default values, you only need
to provide the necessary arguments. Fields with defaults will be automatically
filled in, so you don't have to worry about them unless you explicitly want to
override them.

Packing data
^^^^^^^^^^^^

Packing is the process of converting your structured data into a binary format.
This is similar to Python's `struct <https://docs.python.org/3/library/struct.html>`_
module, but with the added benefit of working directly with Python classes and attributes.

>>> obj = RGB(r=1, g=2, b=3)
>>> pack(obj) # equivalent to pack(obj, RGB), reads as 'pack obj from RGB'
b'\x01\x02\x03'

Notice that in the Python version, you don't need to explicitly provide the struct (i.e., :code:`RGB`)
because *Caterpillar* handles it automatically.

Unpacking data
^^^^^^^^^^^^^^

Recreating data from binary streams is as easy as serializing objects. You just
need to specify the struct that corresponds to the binary data you're working
with.


>>> unpack(RGB, b"\x01\x02\x03") # reads as 'unpack RGB from data'
RGB(r=1, g=2, b=3)

Now that you've seen how to define, pack, and unpack data with structs in *Caterpillar*, you're
almost ready to start working with more complex data structures. And remember,
we've just scratched the surface—there's a lot more to explore!