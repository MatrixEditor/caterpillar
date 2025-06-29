.. _datamodel_processing:

Processing-related Types
========================


Field
-----

The next core element of this library is the *Field*. It serves as a context storage to store configuration data
about a struct. Even sequences and structs can be used as fields. The process is straightforward: each custom operator
creates an instance of a :class:`~caterpillar.fields.Field` with the applied configuration value. Most of the time, this value can be
static or a :ref:`context_lambda`. A field implements basic behavior that should not be duplicated, such as
conditional execution, exception handling with default values, and support for a built-in switch-case structure.

As mentioned earlier, some primitive structs depend on being linked to a :class:`~caterpillar.fields.Field`. This is because all
configuration elements are stored in a :class:`~caterpillar.fields.Field` instance rather than in the target struct instance. More
information about each supported configuration can be found in :ref:`operators`.

.. _greedy:

Greedy
------

This library provides direct support for *greedy* parsing. Leveraging Python's syntactic features, this special form
of parsing is enabled using the `Ellipsis`_ (:code:`...`). All previously introduced structs implement greedy parsing
when enabled.

>>> field = uint8[...]

This special type can be used in places where a length has to be specified. Therefore, it can be applied to all array
:code:`[]` declarations and constructors that take the length as an input argument, such as :class:`CString`, for
example.

.. code-block:: python

    >>> field = Field(CString(...))
    >>> unpack(field, b"abcd\x00")
    'abcd'

.. _prefixed:

Prefixed
--------

In addition to greedy parsing, this library supports prefixed packing and unpacking as well. With *prefixed*, we refer
to the length of an array of elements that should be parsed. In this library, the :code:`slice` class is to achieve a
prefix option.

>>> field = CString[uint32::]


.. _context-reference:

Context
-------

The context is another core element of this framework, utilized to store all relevant variables needed during the
process of packing or unpacking objects. The top-level :meth:`~caterpillar.model.unpack` and :meth:`~caterpillar.model.pack` methods are designed to
create the context themselves with some pre-defined (internal) fields.

.. admonition:: Implementation Note

    :class:`Context` objects are essentially :code:`dict` objects with enhanced capabilities. Therefore, all
    operations supported on dictionaries are applicable.

The context enables special attribute-like access using :code:`getattr` if the attribute wasn't defined in the
instance directly. All custom attributes are stored in the dictionary representation of the instance.

.. attribute:: CTX_PARENT
    :value: "_parent"

    All :class:`Context` instances *SHOULD* contain a reference to the parent context. If the returned reference is
    :code:`None`, it can be assumed that the current context is the root context. If this attribute is set, it
    *MUST* point to a :class:`Context` instance.

.. attribute:: CTX_OBJECT
    :value: "_obj"

    When packing or unpacking objects, the current object attributes are stored within the *object* context. This
    is a special context that allows access to previously parsed fields or attributes of the input object. To
    minimize the number of calls using this attribute, a shortcut named :code:`this` was defined, which
    automatically inserts a path to the object context.


.. attribute:: CTX_STREAM
    :value: "_io"

    The input or output stream *MUST* be set in each context instance to prevent access errors on missing stream
    objects.

    .. seealso::
        Discussion on `Github <https://github.com/MatrixEditor/caterpillar/discussions/1>`_ why this attribute has
        to be set in every context instance.

.. attribute:: CTX_PATH
    :value: "_path"

    Although it is optional to provide the current parsing or building path, it is *recommended*. All nesting
    structures implement a behavior that automatically adds a sub-path while packing or unpacking. Special
    names are :code:`"<root>"` for the starting path and :code:`"<NUMBER>"` for greedy sequence elements.

.. attribute:: CTX_FIELD
    :value: "_field"

    In case a struct is linked to a field, the :class:`~caterpillar.fields.Field` instance will always set this context variable
    to be accessible from within the underlying struct.


.. attribute:: CTX_INDEX
    :value: "_index"

    When packing or unpacking collections of elements, the current working index is given under this context
    variable. This variable is set only in this specific situation.


.. attribute:: CTX_VALUE
    :value: "_value"

    In case a switch-case statement is activated in a field, the context will receive the parsed value in this
    context variable temporarily.

.. attribute:: CTX_POS
    :value: "_pos"

    Currently undefined.

.. attribute:: CTX_OFFSETS
    :value: "_offsets"

    **Internal use only:** This special member is only set in the root context and stores all packed objects that
    should be placed at an offset position.

.. attribute:: CTX_ROOT
    :value: "_root"

    .. versionadded:: 2.5.0

    Special attribute set to specify the root context. If this attribute is not present, the current ``Context`` instance
    will be returned.


Context path
------------

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




.. _Ellipsis: https://docs.python.org/3/library/constants.html#Ellipsis