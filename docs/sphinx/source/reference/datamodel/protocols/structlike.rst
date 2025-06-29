.. _ref_datamodel_protocol_structlike:

Struct-Like Objects
===================


The :class:`_StructLike` protocol can be used to emulate struct types. Even though, :func:`pack`
and :func:`unpack` allow so-called *partial* struct-like objects, there won't be a conversion
within struct class definitions. It is always recommended to implement all methods conforming
to the :code:`_StructLike` protocol.

Special Methods for Struct-Like objects
---------------------------------------

.. method:: object.__pack__(self, obj, context) -> None

        Invoked to serialize the given object into an output stream, :meth:`~object.__pack__`
        is designed to implement the behavior necessary for packing a collection of elements
        or a single element. Accordingly, the input obj may be an :code:`Iterable` or a
        singular element.

        The absence of a standardized implementation for deserializing a collection of elements
        is deliberate. For example, all instances of the :class:`PyStructFormattedField` utilize the Python
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
    struct classes — namely, :class:`~caterpillar.model.Sequence`, :class:`~caterpillar.model.Struct`, and
    :class:`~caterpillar.fields.Field`.

    .. versionchanged:: beta
        The *stream* parameter has been removed and was instead moved into the context.


.. method:: object.__size__(self, context)

    This method serves the purpose of determining the space occupied by this struct,
    expressed in bytes. The availability of a context enables the execution of a
    :class:`_ContextLambda`, offering support for dynamically sized structs. Furthermore,
    for the explicit definition of dynamic structs, the option to raise a :class:`DynamicSizeError`
    is provided.

.. _struct_type:

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
    or sequence definition. The type of the stored value must be conforming to the :class:`_StructLike` protocol.


Template Containers
^^^^^^^^^^^^^^^^^^^

.. attribute:: class.__template__

    All template classes store information about the used template type variables. Whether they
    are required or just positional. In addition, default inferred types are stored as well.


Protocols for Struct-like objects
---------------------------------

To represent a :code:`_StructLike` object, all previously described methods must be implemented:

.. py:class:: _StructLike[_IT, _OT]

    .. py:function:: __pack__(self, obj: _IT, context: _ContextLike) -> None
                     __unpack__(self, context: _ContextLike) -> _OT
                     __size__(self, context: _ContextLike) -> int


.. py:class:: _ContainsStruct[_IT, _OT]

    .. py:attribute:: __struct__
        :type: _StructLike[_IT, _OT]


.. py:class:: _SupportsPack[_IT]

    .. py:function:: __pack__(self, obj: _IT, context: _ContextLike) -> None


.. py:class:: _SupportsUnpack[_OT]

    .. py:function:: __unpack__(self, context: _ContextLike) -> _OT


.. py:class:: _SupportsSize

    .. py:function:: __size__(self, context: _ContextLike) -> int


.. py:class:: _SupportsType

    .. py:function:: __type__(self) -> Optional[type | str]



.. _struct: https://docs.python.org/3/library/struct.html
.. _sphinx-autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html