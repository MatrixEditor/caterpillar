.. _datamodel:

**********
Data Model
**********

.. _objects:

:dfn:`Structs` serve as the foundation of this library. All data within the framework
undergoes the process of packing and unpacking using structs or :class:`~caterpillar.abc._StructLike`
objects. There are three possible types of structs:

* *Sequences*:
    These structs operate independently of fields, making them field-agnostic. As
    such, they do not need to be attached to a :class:`~caterpillar.fields.Field` instance. Typically,
    they are are combined with specific requirements, which will be discussed later
    on.

* *Primitive Structs*:
    All defined primitive structs depent on being linked to a :class:`~caterpillar.fields.Field`
    instance. They are designed to incorporate all attributes that can be set
    on a field.

* *Partial Structs*:
    For scenarios where selective functionality is paramount, it is recommended
    to implement structs that focus solely on parsing, writing, or the calculation
    of the struct's size. These specialized structs, referred to as *partial structs*,
    provide a modular approach for extending the library. Consideration of partial
    structs is essential when aiming to extend the capabilities of this framework.


.. toctree::
    :caption: Standard Data Model

    datamodel/standard


.. toctree::
    :caption: Caterpillar-specific Protocols

    datamodel/protocols.rst

.. toctree::
    :hidden:

    datamodel/processing_classes.rst



.. _struct: https://docs.python.org/3/library/struct.html
.. _sphinx-autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _Ellipsis: https://docs.python.org/3/library/constants.html#Ellipsis