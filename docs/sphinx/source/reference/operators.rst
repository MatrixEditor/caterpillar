.. _operators:

*********
Operators
*********

*TODO: describe all supported operators*

*Caterpillar* supports various operators for :class:`~caterpillar.model.Sequence`,
:class:`~caterpillar.model.Struct`, :class:`Field`, and custom struct implementations
[1]_. This section provides an overview of the operators that can be used with
structs, including special context operations.

Struct operators
----------------

All functions described below return a new :class:`Field` instance if not already
called on a field object.

.. function:: struct.__getitem__(self, length)

    This function acts as an array definition and supports different kinds of length
    types.


    Static (``int``)
        A constant value is used to mark static arrays with a fixed length. Float
        values are not accepted.

        >>> array = uint8[100]

    Dynamic (:class:`_ContextLambda`)
        A callable function may be used to return the length as an integer. If you choose
        not to use a context value, the provided callable function must take the :class:`Context`
        instance as its first argument.

        >>> array = uint8[this.length] # where this.length would store 100

    :ref:`greedy` (:class:`_GreedyType`)
        Used when the amount of elements to be unpacked is unknown. The struct tries to
        unpack an object of the given type and stops either on EOF or if an exception
        is thrown.

        >>> array = uint8[...]

    :ref:`prefixed` (:class:`_PrefixedType`, :code:`slice`)
        In cases where there are length-prefixed structures and you don't want to store the
        length in an extra variable, you can use :class:`Prefixed` to improve packing data.

        >>> prefixed_array = CString[uint8::]

    .. note::
        This function is applicable to all classes annotated with :code:`@struct` or
        :code:`@bitfield`.


.. function:: struct.__rshift__(self, options)

    Invoked to apply a set of options to a :class:`Field`. This function changes the behavior
    of a struct. It unpacks a value using the field's underlying struct and passes it directly
    into the given options to retrieve the final struct.

    The described behavior has a limitation: if the underlying struct is not a :class:`_ContextLambda`,
    there is no possibility of packing an object back to binary data because the initial value is not
    known.

    >>> field = Field(this.foo) >> {
    ...     "bar": uint16,
    ...     "baz": uint32,
    ... }

    You can also include a default option using :attr:`!DEFAULT_OPTION` from within the
    :code:`fields` submodule.

    >>> field = Field(this.foo) >> {
    ...     "bar": uint16,
    ...     DEFAULT_OPTION: ctx._value
    ... }

    The previously parsed value is accessible from within the current context, not the
    current object context.


.. function:: struct.__matmul__(self, offset)

    Another special operator (:code:`@`) is used to re-position the current field to a specified offset
    position, where the offset can be static or dynamic.

    When unpacking objects from a stream, the reader will temporarily jump to the given offset. Using the
    :attr:`!F_KEEP_POSITION` option, the reader will continue parsing at the resulting position.

    Packing is tricky as we don't want to lose any data when jumping to an offset position. Internally, a
    dictionary with offset-data mappings is created and will be applied when all normal fields have been
    written to the stream. Alternatively, there is an option to firstly write everything into a temporary
    file and copy the final result into the given stream.


    Static (:code:`int`)
        Integer values are accepted to be static, and therefore the default behaviour is applied.

        >>> field = uint8 @ 0x1234

    Dynamic (:class:`_ContextLambda`)
        Callables and context lambdas are accepted as well.

        >>> field = uint8 @ this.offset

    .. caution::
        This operator is not applicable on raw struct classes. Therefore, the class has to be turned into
        a field first. A shortcut can help you with that.

        >>> from caterpillar.shortcuts import F
        >>> field = F(Format) @ 0x1233


.. function:: struct.__floordiv__(self, condition)

    *Experimental.* Invoked to link the current field or struct with a certain condition,
    which can be either a static boolean value or a context lambda.

    >>> field = uint8 // (lenof(this.array) > 0)

    .. admonition:: Developer's note

        This feature is proposed to be replaced by an if-else structure chain in the future.


.. function:: struct.__rsub__(self, bits)

    Invoked to specify the amount of bits this field uses. (Only applicable in classes decorated with
    :code:`@bitfield`)

    >>> field = 3 - uint8   # 3 of 8 bits are used


.. function:: struct.__and__(self, other)

    Invoked to create a chain of two structs. It is important that only the last element doesn't need
    to return a :code:`bytes` object after unpacking.

    >>> chain = ZLibCompressed(...) & Format

    .. important::
        The returned object is **not** a :class:`Field` instance, but a :class:`Chain` instance to
        support more than two elements.



Field specific operations
-------------------------

The following methods are specifically designed for fields and will only affect those. Even though these
operations are also supported on sequence objects, only the returning :class:`Field` object will be affected.

.. function:: field.__or__(self, flag)
.. function:: field.__ior__(self, flag)

    With the logical OR operation, a so-called :class:`Flag` can be set. Some flags are defined globally, and
    their meaning is described in :ref:`options`.

    >>> field = uint8 | F_KEEP_POSITION

.. function:: field.__xor__(self, flag)
.. function:: field.__ixor__(self, flag)

    The logical XOR operation is designed to remove a flag/option from the specified field.

    >>> field = uint8 ^ F_KEEP_POSITION


Sequence specific operators
---------------------------

The following functions have been implemented to provide a user-friendly interface for
extending :class:`~caterpillar.model.Sequence` objects. All subclasses inherit this
functionality as well.

.. function:: sequence.__add__(self, sequence)
.. function:: sequence.__iadd__(self, sequence)

    Called to *import* all fields from the given sequence into this instance. Note that the
    fields will be added to the *end* of the current field list.

    >>> seq = Sequence({"a": uint8}) + Sequence({"b": uint8})

.. function:: sequence.__sub__(self, sequence)
.. function:: sequence.__isub__(self, sequence)

    Invoked to remove all fields in this sequence that are also stored in the given
    sequence. This operation does not alter the used model but only affects the
    internal model representation.

    >>> seq = Sequence({"a": uint8, "b": uint8}) - Sequence({"b": uint8})

Context specific operations
---------------------------

The :class:`Context` implements attribute-like access on top of a dictionary, where the requested
path is resolved recursively. For instance, the path :code:`"foo.bar.baz"` will be split into
three parts and then :code:`getattr` is called until the final element has been reached or an
error occurs.

To enhance the facilities of a :class:`Context` instance, there are special classes with even more
special operations.

Context path
^^^^^^^^^^^^

The context path takes a special place, as it can provide lazy execution of almost all operators
on definition. Its attribute-access model results in a new :class:`ContextPath` instance.

>>> path = ContextPath("foo").bar.baz
Path('foo.bar.baz')

To enable list-like access and function calls, there are special methods:

.. function:: path.__call__(self, **kwargs)

    Calling the path without the context instance results in a special state. The path
    stores the keyword arguments given in the call and executes them after retrieving
    the value from the context.

    >>> path = this.foo.bar(x=19)
    Path('_obj.foo.bar', call(x=10))


.. function:: path.__getitem__(self, key)

    This method has the same effect on the path, as it stores the key argument and executes the
    :meth:`!__getitem__` method on the retrieved value afterward.

    >>> path = this.foo.bar(x=19)[10]
    Path('_obj.foo.bar', call(x=19), getitem(10))


.. admonition::: Developer's note

    The current implementation of :class:`ContextPath` does not allow function calls or list-like
    access between path elements. These special states can only be applied at the end of a path.


.. [1] Custom implementations must extend :class:`FieldMixin` class to be able to use special operators.