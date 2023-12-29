.. _datamodel:

**********
Data Model
**********

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

Standard Types
==============

Below is a list of types provided by *Caterpillar*. These types are designed to maintain
compatibility with older versions of the library, making them particularly important.

Sequence
--------

As previously explained, a sequence functions independently of fields. The library introduces
the :class:`~caterpillar.model.Sequence` as a named finite collection of :class:`Field` objects. A *Sequence*
operates on a model, which is a string-to-field mapping by default. Later, we will discuss
the distinctions between a *Sequence* and a *Struct* regarding the model representation.

A sequence definition entails the specification of a :class:`~caterpillar.model.Sequence` object by directly
indicating the model to use. Inheritance poses a challenge with sequences, as they are not
designed to operate on a type hierarchy. The default instantiation with all default options
involves passing the dictionary with all fields directly:

>>> Format = Sequence({"a": uint8, "b": uint32})

.. admonition:: Programmers Note:

    All sequence types introduced by this library can also store so-called *unnamed* fields.
    These fields are not visible in the unpacked result and are automatically packed, removing
    concerns about them when the option ``S_DISCARD_UNNAMED`` is active. Their names usually
    begin with an underscore and must solely contain numbers (e.g., :code:`_123`).

The sequence follows the :class:`Field` configuration model, allowing sequence and
field-related options to be set. As mentioned earlier, the ``S_DISCARD_UNNAMED`` option can
be used for example to exclude all unnamed fields from the final representation. A complete
list of all configuration options and their impact can be found in :ref:`options`.

All sequences store a configurable :class:`ByteOrder` and :class:`Arch` as architecture,
which are passed to **all** fields in the current model. For more information on why these
classes are not specified as an enum class, please refer to :ref:`byteorder`.

Inheritance in sequences is intricate, as a :class:`~caterpillar.model.Sequence` is constructed from a dictionary
of elements. We can attempt to simulate a chain of extended *base sequences* using the
concatenation of two sequences. The :meth:`~sequence.__add__` method will *import* all fields
from the other specified sequence. The only disadvantage is the placement required by the
operator. For instance:

>>> BaseFormat = Sequence({"magic": b"MAGIC", "a": uint8})
>>> Format = Sequence({"b": uint32, "c": uint16}) + BaseFormat

will result in the following field order:

>>> list(Format.get_members())
['b', 'c', 'magic', 'a']

which is not the intended order. The correct order should be :code:`['magic', 'a', 'b', 'c']`.
This can be achieved by using the :code:`BaseFormat` instance as the first operand.

.. warning::
    This will alter the *BaseFormat* sequence, making it unusable elsewhere as the *base* for
    all sub-sequences. Therefore, it is not recommended to use inheritance within sequences.
    The :class:`~caterpillar.model.Struct` class resolves this issue with ease.

Nesting sequences is allowed by default and can be achieved by incorporating another
:class:`~caterpillar.model.Sequence` into the model. It is important to note that *nesting* is distinct from
*inheritance*, adding an additional layer of packing and unpacking.

>>> Format = Sequence({"other": BaseFormat, "b": uint32})


Struct
^^^^^^

A *struct* describes a finite collection of named fields. In contrast to a *sequence*, a *struct*
utilizes Python classes as its model. The annotation feature in Python enables the definition of
custom types as annotations, enabling this special struct class to create a model solely based on
class annotations. Additionally, it generates a ``dataclass`` of the provided model, offering a
standardized string representation.

Several differences exist between a :class:`~caterpillar.model.Sequence` and a
:class:`~caterpillar.model.Struct`, with the most significant ones highlighted below:


.. list-table:: Behaviour of structs and sequences
    :header-rows: 1
    :widths: 10, 15, 15
    :stub-columns: 1

    * -
      - Sequence
      - Struct
    * - Model Type
      - dict
      - type
    * - Inheritance
      - No
      - Yes
    * - Attribute Access
      - :code:`x["name"]`
      - :code:`getattr(x, "name", None)`
    * - Unpacked Type (also needed to pack)
      - dict [*]_
      - instance of model
    * - Documentation
      - No
      - Yes


.. [*] The unpacked values are stored inside a :class:`Context` instance, a direct subclass of a dictionary.

As evident from the comparison, the :class:`~caterpillar.model.Struct` class introduces new features such as
inheritance and documentation support. It's crucial to note that inheritance uses
struct types exclusively.

The :class:`~caterpillar.model.Sequence` class implements a specific process for creating an internal representation
of the given model. The :class:`~caterpillar.model.Struct` class enhances this process by handling default values, replacing
types for documentation purposes, or removing annotation fields directly from the model. Additionally,
this class adds :attr:`~class.__struct__` to the model afterward.

.. admonition:: Implementation Note

    If you decide to use the ``annotation`` feature from the ``__future__`` module, it is necessary to
    enable :attr:`~options.S_EVAL_ANNOTATIONS` since it "`Stringizes`_" all annotations. ``inspect`` then
    evaluates all strings, introducing a potential security risk. Exercise with caution when evaluating code!

Specifying structs is as simple as defining `Python Classes`_:

>>> @struct
... class BaseFormat:
...     magic: b"MAGIC"
...     a: uint8
...

Internally, a representation with all required fields and their corresponding names is
created. As :code:`b"MAGIC"` or :code:`uint8` are instances of types, the type replacement
for documentation purposes should be enabled, as shown in :ref:`struct_type`.

As described above, this class introduces an easy-to-use inheritance system using the method
resolution order of Python:

>>> @struct
... class Format(BaseFormat):
...     b: uint32
...     c: uint16
...
>>> list(Format.__struct__.get_members())
['magic', 'a', 'b', 'c']

.. admonition:: Programmers Note

    As the :class:`~caterpillar.model.Struct` class is a direct subclass of :class:`~caterpillar.model.Sequence`, nesting is supported
    by default. That means, so-called *anonymous inner* structs can be defined within a class
    definition.

    >>> @struct
    ... class Format:
    ...     a: uint32
    ...     b: {"c": uint8}
    ...

    It is not recommended to use this technique as the inner structs can't be used anywhere else.
    Anonymous inner union definitions are tricky and are not officially supported yet. There are
    workarounds to that problem, which are discussed in the API documentation of :class:`~caterpillar.model.Sequence`.


.. _union-reference:

Union
^^^^^

Internally constructing unions in the library poses challenges. The current implementation uses
the predefined behavior of the :class:`~caterpillar.model.Sequence` class for union types. It selects the field with
the greatest length as its representational size. *Unions*, much like *BitFields*, must store a static
size.

**In essence, they behave similarly to C unions.** A traditional function hook will be installed on
the model to capture field assignments. What that means will be illustrated by the following example:

>>> @union
... class Format:
...     foo: uint16
...     bar: uint32
...     baz: boolean
...
>>> obj = Format()      # union does not need any values

Right now, all attributes store the default value (:code:`None`). If we assign a new value to one field, it
will be applied to all others. Hence,

>>> obj.bar = 0xFF00FF00

will result in

>>> obj
Format(foo=65280, bar=4278255360, baz=False)


.. admonition:: Implementation Detail

    The constructor is the only place where there is no synchronization between fields. Additionally, the current
    implementation may produce some overhead, because every *refresh* will first pack the new value and then
    executes *unpack* on all other fields.

BitField
^^^^^^^^

A *BitField*, despite its name suggesting a field of bits, is a powerful structure designed for
detailed byte inspection. Similar to other structures, it is a finite collection of named fields. This
section will introduce potential challenges associated with the implementation of a :class:`~caterpillar.model.BitField`
and explains its behavior.

.. caution::
    This class is still experimental, and caution is advised. For a list of known disadvantages or
    problems, refer to the information provided below.

As mentioned earlier, a *BitField* allows the inspection of individual bits within parsed bytes. Its
internal model relies on a special function or attribute, namely :meth:`~object.__bits__`. Consequently,
a bitfield has a predefined length and will always possess a length that can be represented in bytes.

The :class:`~caterpillar.model.BitField` class not only stores the existing model representation with a name-to-field
mapping and a collection of all fields but also introduces a special organizational class:
:class:`~caterpillar.model.BitFieldGroup`. Each group defines its bit size, the absolute bit position in the bitfield,
and a mapping of fields to their relative bit position in the current group, along with the field's
width. In the following example, three groups are created:

>>> @bitfield
... class Format:
...     a : uint8           # Group 1, pos=0, size=8
...     _ : 0               # Group 2, pos=8, size=8
...     b : 15 - uint16     # \
...     c : 1               #  \ Group 3, pos=16, size=16
...

- ``a``: The first field creates a group with a size of eight bits at position zero.
- ``_``: Next, a zero-sized field indicates that padding until the end of the current byte should be
  added. As we start from bit position ``0``, one byte will be filled with zeros.
- ``b``: The third field only uses 15 bits of a 16-bit wide field (2 bytes inferred using :code:`uint16`)
- ``c``: The last field uses the final bit of our current group.

*TODO: describe process of collecting fields, packing and unpacking*


Field
-----

The next core element of this library is the *Field*. It serves as a context storage to store configuration data
about a struct. Even sequences and structs can be used as fields. The process is straightforward: each custom operator
creates an instance of a :class:`Field` with the applied configuration value. Most of the time, this value can be
static or a :ref:`context_lambda`. A field implements basic behavior that should not be duplicated, such as
conditional execution, exception handling with default values, and support for a built-in switch-case structure.

As mentioned earlier, some primitive structs depend on being linked to a :class:`Field`. This is because all
configuration elements are stored in a :class:`Field` instance rather than in the target struct instance. More
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

    In case a struct is linked to a field, the :class:`Field` instance will always set this context variable
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
    of multiple elements concurrently. By default, the :class:`Field` class stores all essential
    attributes required to determine the length of elements set for unpacking. The :meth:`~__unpack__`
    method is activated through the :code:`unpack()` operation, integrated with the default
    struct classes — namely, :class:`~caterpillar.model.Sequence`, :class:`~caterpillar.model.Struct`, and :class:`Field`.

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

    >>> struct = BigEndian | struct # Automatically sets __byteorder__


.. method:: object.__set_byteorder__(self, byteorder)

    In contrast to the attribute :attr:`~object.__byteorder__`, the :meth:`~object.__set_byteorder__`
    method is invoked to apply the current byteorder to a struct. The default behavior,
    as described in :class:`FieldMixin`, is to return a new :class:`Field` instance with
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
.. _Stringizes: https://docs.python.org/3/howto/annotations.html#manually-un-stringizing-stringized-annotations
.. _Python Classes: https://docs.python.org/3/reference/compound_stmts.html#class
.. _Ellipsis: https://docs.python.org/3/library/constants.html#Ellipsis