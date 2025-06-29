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

.. _context_lambda:

Context lambda
^^^^^^^^^^^^^^

Dynamic sized structs are supported by this library using the power of so-called *context lambdas*. This library
introduces a special callable :class:`_ContextLambda`, that takes a :class:`Context` instance and returns the
desired result. To mimic a *context lambda*, the :meth:`__call__` method has to be implemented.

Dynamic-sized structs are supported by this library using the power of so-called *context lambdas*. This library
introduces a special callable :class:`_ContextLambda` that takes a :class:`Context` instance and returns the #
desired result. To mimic a *context lambda*, the :meth:`__call__` method has to be implemented.

.. function:: object.__call__(self, context)

    This library does not distinguish between callable objects and *context lambdas*. They are treated as the
    same class (this aspect is under subject to changes).


Context path
^^^^^^^^^^^^

The path of a context is a specialized form of a :ref:`context_lambda` and supports lazy evaluation of most
operators (conditional ones excluded). Once called, they try to retrieve the requested value from within
the given :class:`Context` instance. Below is a list of default paths designed to provide a relatively easy
way to access the context variables.

.. attribute:: ctx
    :value: ""

    This special path acts as a wrapper to access all variables within the top-level :class:`Context` object.

.. attribute:: this
    :value: "_obj"

    As described before, a special *object context* is created when packing or unpacking structs that store
    more than one field.

.. attribute:: parent
    :value: "_parent._obj"

    A shortcut to access the object context of the parent context.




Special method names
====================

A class can either extend :class:`_StructLike` or implement the special methods needed
to act as a struct. The subsequent sections provide an overview of all special methods
and attributes introduced by this library. Further insights into extending structs with
custom operators can be found in  :ref:`operators`.

Emulating Struct Types
----------------------

.. method:: object.__pack__(self, obj, context)

    Invoked to serialize the given object into an output stream, :meth:`~object.__pack__`
    is designed to implement the behavior necessary for packing a collection of elements
    or a single element. Accordingly, the input obj may be an :code:`Iterable` or a
    singular element.

    The absence of a standardized implementation for deserializing a collection of elements
    is deliberate. For example, all instances of the :class:`FormatField` utilize the Python
    library `struct`_ internally to pack and unpack data. To optimize execution times, a
    collection of elements is packed and unpacked in a single call, rather than handling each
    element individually.

    The context must incorporate specific members, mentioned in :ref:`context`. Any data
    input verification is implemented by the corresponding class.

    :meth:`~__pack__` is invoked by the :code:`pack()` method defined within this library.
    Its purpose is to dictate how input objects are written to the stream. It is crucial
    to note that the outcome of this function is ignored.

    .. versionchanged:: beta
        The *stream* parameter has been removed and was instead moved into the context.

.. method:: object.__unpack__(self, context)

    Called to desersialize objects from an input stream (the stream is stored in the given context).
    The result of :meth:`~object.__unpack__` is not going to be ignored.

    Every implementation is tasked with the decision of whether to support the deserialization
    of multiple elements concurrently. By default, the :class:`~caterpillar.fields.Field` class stores all essential
    attributes required to determine the length of elements set for unpacking. The :meth:`~__unpack__`
    method is activated through the :code:`unpack()` operation, integrated with the default
    struct classes — namely, :class:`~caterpillar.model.Sequence`, :class:`~caterpillar.model.Struct`, and :class:`~caterpillar.fields.Field`.

    .. versionchanged:: beta
        The *stream* parameter has been removed and was instead moved into the context.

.. method:: object.__size__(self, context)

    This method serves the purpose of determining the space occupied by this struct,
    expressed in bytes. The availability of a context enables the execution of a
    :class:`_ContextLambda`, offering support for dynamically sized structs. Furthermore,
    for the explicit definition of dynamic structs, the option to raise a :class:`DynamicSizeError`
    is provided.


.. _struct_type:

Customizing the struct's type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. method:: object.__type__(self)

    The configuration of *Structs* incorporates type replacement before a dataclass is
    created. This feature was specifically introduced for documentation purposes.
    The optional :meth:`~object.__type__` method allows for the specification of a
    type, with the default being :code:`Any` if not explicitly defined.

    .. note::
        The implementation of the :meth:`~object.__type__` method is optional and,
        therefore, not mandatory as per the library's specifications.

    The following example demonstrates the use of the `sphinx-autodoc`_ extension to document
    struct classes with the :code:`S_REPLACE_TYPE` option enabled. Only documented members
    are displayed.

    .. code-block:: rst

        .. autoclass:: examples.formats.nibarchive.NIBHeader()
            :members:

    Will be displayed as:

    .. autoclass:: examples.formats.nibarchive.NIBHeader()
        :members:
        :no-undoc-members:

    In this illustration, the extra parentheses at the end are included to prevent the
    automatic creation of constructors.


Struct containers
^^^^^^^^^^^^^^^^^

.. attribute:: class.__struct__

    All models annotated with either :code:`@struct` or :code:`@bitfield` fall into the
    category of *struct containers*. These containers store the additional class attribute
    :func:`~class.__struct__`.

    Internally, any types utilizing this attribute can be employed within a struct, bitfield,
    or sequence definition. The type of the stored value must be a subclass of :class:`_StructLike`.


Template Containers
^^^^^^^^^^^^^^^^^^^

.. attribute:: class.__template__

    All template classes store information about the used template type variables. Whether they
    are required or just positional. In addition, default inferred types are stored as well.

BitField specific methods
-------------------------

The introduced :class:`~caterpillar.model.BitField` class is special in many different ways. One key
attribute is its fixed size. To determine the size of a struct, it leverages a special
member, which can be either a function or an attribute.

.. method:: object.__bits__(self)

    Called to measure the bit count of the current object. :meth:`~object.__bits__`
    serves as the sole requirement for the defined fields in the current implementation
    of the :class:`~caterpillar.model.BitField` class.

    .. note::
        This class member can also be expressed as an attribute. The library automatically
        adapts to the appropriate representation based on the context.


Customizing the object's byteorder
----------------------------------

.. attribute:: object.__byteorder__

    The byteorder of a struct can be temporarily configured using the corresponding
    operator. It is important to note that this attribute is utilized internally and
    should not be used elsewhere.

    .. code-block:: python

        >>> struct = BigEndian | struct # Automatically sets __byteorder__


.. method:: object.__set_byteorder__(self, byteorder)

    In contrast to the attribute :attr:`~object.__byteorder__`, the :meth:`~object.__set_byteorder__`
    method is invoked to apply the current byteorder to a struct. The default behavior,
    as described in :class:`FieldMixin`, is to return a new :class:`~caterpillar.fields.Field` instance with
    the byteorder applied. Note the use of another operator here.

    >>> field = BigEndian + struct


Modifying fields
----------------

.. attribute:: field.__name__

    The name of a regular field is not explicitly specified in a typical attribute but is
    instead set using a dedicated one. This naming convention is automatically applied by
    all default :class:`~caterpillar.model.Sequence` implementations. The name can be retrieved through the
    use of :code:`field.__name__`.


.. _struct: https://docs.python.org/3/library/struct.html
.. _sphinx-autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _Ellipsis: https://docs.python.org/3/library/constants.html#Ellipsis