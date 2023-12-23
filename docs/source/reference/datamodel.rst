.. _datamodel:

**********
Data Model
**********

*TODO: add documentation and behaviour explanation*

.. _objects:

Structs, Sequences and Fields
=============================

:dfn:`Structs` serve as the foundation of this library. All data within the framework
undergoes the process of packing and unpacking using structs or :class:`_StructLike`
objects. There are three possible types of structs:

* *Sequences*:
    These structs operate independently of fields, making them field-agnostic. As
    such, they do not need to be attached to a :class:`Field` instance. Typically,
    they are are combined with specific requirements, which will be discussed later
    on.

* *Primitive Structs*:
    All defined primitive structs depent on being linked to a :class:`Field`
    instance. They are designed to incorporate all attributes that can be set
    on a field.

* *Partial Structs*:
    For scenarios where selective functionality is paramount, it is recommended
    to implement structs that focus solely on parsing, writing, or the calculation
    of the struct's size. These specialized structs, referred to as *partial structs*,
    provide a modular approach for extending the library. Consideration of partial
    structs is essential when aiming to extend the capabilities of this framework.


Special method names
====================

A class can either extend :class:`_StructLike` or implement the special methods needed
to act as a struct. The subsequent sections provide an overview of all special methods
and attributes introduced by this library. Further insights into extending structs with
custom operators can be found in  :ref:`operators`.

Emulating Struct Types
----------------------

.. method:: object.__pack__(self, obj, stream, context)

    Invoked to serialize the given object into an output stream, :meth:`~object.__pack__`
    is designed to implement the behavior necessary for packing a collection of elements
    or a single element. Accordingly, the input obj may be an :code:`Iterable` or a
    singular element.

    The absence of a standardized implementation for deserializing a collection of elements
    is deliberate, enhancing the library's adaptability. For example, all instances of the
    :class:`FormatField` utilize the Python library `struct`_ internally to pack and unpack
    data. To optimize execution times, a collection of elements is packed and unpacked in a
    single call, rather than handling each element individually.

    The context must incorporate specific members, mentioned in :ref:`context`. Any data
    input verification is implemented by the corresponding class.

    :meth:`~__pack__` is invoked by the :code:`pack()` method defined within this library.
    Its purpose is to dictate how input objects are written to the stream. It is crucial
    to note that the outcome of this function is ignored.

.. method:: object.__unpack__(self, stream, context)

    Called to desersialize objects from an input stream. The result of :meth:`~object.__unpack__`
    won't be ignored.

    Every implementation is tasked with the decision of whether to support the deserialization
    of multiple elements concurrently. By default, the :class:`Field` class stores all essential
    attributes required to determine the length of elements set for unpacking. The :meth:`~__unpack__`
    method is activated through the :code:`unpack()` operation, integrated with the default
    struct classes — namely, :class:`Sequence`, :class:`Struct`, and :class:`Field`.

.. method:: object.__size__(self, context)

    This method serves the purpose of determining the space occupied by this struct,
    expressed in bytes. The availability of a context enables the execution of a
    :class:`_ContextLambda`, offering support for dynamically sized structs. Furthermore,
    for the explicit definition of dynamic structs, the option to raise a :class:`DynamicSizeError`
    is provided.

Customising the struct's type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. method:: object.__type__(self)

    The configuration of *Structs* incorporates type replacement before a dataclass is
    created. This feature was specifically introduced for documentation purposes.
    The optional :meth:`~object.__type__` method allows for the specification of a
    type, with the default being :code:`Any` if not explicitly defined.

    .. note::
        The implementation of the :meth:`~object.__type__` method is optional and,
        therefore, not mandatory as per the library's specifications.

    The following example demonstrates the use of the `sphinx-autodoc`_ tool to document
    struct classes with the :code:`S_REPLACE_TYPE` option enabled. Only documented members
    are displayed.

    .. code-block:: rst

        .. autoclass:: examples.nibarchive.NIBHeader()
            :members:

    Will be displayed as:

    .. autoclass:: examples.nibarchive.NIBHeader()
        :members:
        :no-undoc-members:

    In this illustration, the extra parentheses at the end are included to prevent the
    automatic creation of constructors.

*TODO*

.. attribute:: object.__struct__

.. method:: object.__bits__(self)

.. attribute:: object.__byteorder__

.. method:: object.__set_byteorder__(self, byteorder)

.. attribute:: field.__name__

.. _struct: https://docs.python.org/3/library/struct.html
.. _sphinx-autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html