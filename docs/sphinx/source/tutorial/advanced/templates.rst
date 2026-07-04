.. _tutorial-templates:

Templates
=========

.. versionchanged:: 2.9.0
    Added support for Python's :class:`Generic` and :class:`TypeVar` types.

Templates are blueprints for binary structures. They let you describe a layout
once and specialize it with different Caterpillar field types later.

The preferred form uses Python generics. Legacy ``TemplateTypeVar`` templates
are still supported and are covered at the end of this page.

If you'd like the implementation details, see :ref:`ref-templates`.

Generic Templates
-----------------

Define a template as a normal generic Python class and decorate it with
``@template``. A plain type variable annotation is enough.

.. code-block:: python
    :caption: A generic scalar template

    from typing import Generic, TypeVar

    from caterpillar.py import pack, template, uint8, uint16

    T = TypeVar("T")


    @template
    class Box(Generic[T]):
        value: T


    ByteBox = Box[uint8]
    WordBox = Box[uint16]

    assert pack(ByteBox(7)) == b"\x07"
    assert pack(WordBox(0x0203)) == b"\x03\x02"

``Box`` is not a struct by itself. ``Box[uint8]`` materializes a concrete
struct class and caches it, so repeated uses of the same specialization return
the same class.

Multiple Type Variables
-----------------------

Templates can use more than one type variable. The order in ``Generic[...]``
defines the positional specialization order.

.. code-block:: python
    :caption: Multiple template parameters

    from typing import Generic, TypeVar

    from caterpillar.py import BigEndian, pack, template, uint8, uint16

    T = TypeVar("T")
    U = TypeVar("U")


    @template
    class Pair(Generic[T, U]):
        left: T
        right: U


    ByteWordPair = Pair[uint8, uint16]
    obj = ByteWordPair(1, 0x0203)

    assert pack(obj, order=BigEndian) == b"\x01\x02\x03"

Fields With Layout Metadata
---------------------------

Use direct ``T`` annotations for simple scalar fields. When a field needs
Caterpillar-specific layout metadata, keep the Python type in the first
position of ``f[]`` and put the template field marker in the metadata position.

.. code-block:: python
    :caption: Repeated template field

    from typing import Generic, TypeVar

    from caterpillar.py import f, field_of, pack, template, uint8

    T = TypeVar("T")


    @template
    class Vector(Generic[T]):
        values: f[list[T], field_of(T)[2]]


    ByteVector = Vector[uint8]

    assert pack(ByteVector([3, 4])) == b"\x03\x04"

``field_of(T)`` supports the same layout operators as normal fields, including
sequence length, offset, switch mappings, byte order, bit width, and condition
markers. For example, ``field_of(T)[2]`` becomes a two-element field after
specialization.

Partial Templates
-----------------

A specialization that still contains unresolved type variables remains a
template. This is useful for fixing only part of a layout.

.. code-block:: python
    :caption: Partial generic specialization

    from typing import Generic, TypeVar

    from caterpillar.py import BigEndian, pack, template, uint8, uint16

    T = TypeVar("T")
    U = TypeVar("U")


    @template
    class Pair(Generic[T, U]):
        left: T
        right: U


    BytePair = Pair[uint8, U]
    ByteWordPair = BytePair[uint16]

    assert pack(ByteWordPair(1, 0x0203), order=BigEndian) == b"\x01\x02\x03"

Subclassing Specializations
---------------------------

Template specializations are normal struct classes and can be used as bases for
other structs.

.. code-block:: python
    :caption: Extending a specialization

    from typing import Generic, TypeVar

    from caterpillar.py import BigEndian, f, pack, struct, template, uint8, uint16

    T = TypeVar("T")


    @template
    class Box(Generic[T]):
        value: T


    @struct
    class Packet(Box[uint8]):
        tail: f[int, uint16]


    assert pack(Packet(1, 0x0203), order=BigEndian) == b"\x01\x02\x03"

Legacy Templates
----------------

The older ``TemplateTypeVar`` style is still supported. Use it when maintaining
existing code that already depends on ``derive()``.

.. code-block:: python
    :caption: Legacy template definition

    from caterpillar.py import TemplateTypeVar, derive, template, uint8, uint16

    A = TemplateTypeVar("A")


    @template(A, "B")
    class FormatTemplate:
        foo: A
        bar: B


    Format = derive(FormatTemplate, uint8, uint16)

``derive()`` remains available as an explicit escape hatch for generic
templates as well, but direct subscript syntax is the preferred form for new
code.
