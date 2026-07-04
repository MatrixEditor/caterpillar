.. _ref-templates:

Templates
=========

.. versionchanged:: 2.9.0
    Added support for Python's builtin :class:`TypeVar``

Templates are generic model classes that become concrete struct classes after
specialization. A template class stores template metadata on ``__template__``
and does not store ``__struct__`` until it is specialized.

Caterpillar supports two template systems:

* Python generic templates, the preferred API for new code.
* Legacy ``TemplateTypeVar`` templates, kept for compatibility.

Python Generic Templates
------------------------

Generic templates use normal Python ``TypeVar`` objects and ``Generic`` bases.

.. code-block:: python

    from typing import Generic, TypeVar

    from caterpillar.py import template, uint8

    T = TypeVar("T")


    @template
    class Box(Generic[T]):
        value: T


    ByteBox = Box[uint8]

``Box`` is a template. ``Box[uint8]`` is a concrete struct class. Caterpillar
installs ``__class_getitem__`` on the template class and materializes the
specialization when it is subscripted.

Specialization performs two different substitutions:

* In normal Python type positions, Caterpillar field objects are replaced with
  their Python value type using ``typeof()``.
* In field metadata positions, Caterpillar keeps the actual field object and
  builds a ``Field`` from it.

For example:

.. code-block:: python

    @template
    class Box(Generic[T]):
        value: T


    ByteBox = Box[uint8]

``value: T`` is converted to a ``Field(uint8)`` before the generated class is
passed to :class:`~caterpillar.model.Struct`.


**Layout Metadata With** ``f[]``

``f[]`` is Caterpillar's public spelling for ``typing.Annotated[]``. Use it
when the Python value type and the binary layout metadata must both be present.

.. code-block:: python

    from typing import Generic, TypeVar

    from caterpillar.py import f, field_of, template, uint8

    T = TypeVar("T")


    @template
    class Vector(Generic[T]):
        values: f[list[T], field_of(T)[2]]


    ByteVector = Vector[uint8]

In this example, the Python-facing type becomes ``list[int]`` while the binary
layout metadata becomes a two-element ``Field(uint8)``.

``field_of(T)`` supports the same layout operators as
:class:`~caterpillar.model.TemplateTypeVar`: sequence length, offset, switch
options, byte order, bit width, and condition. Generic specializations are cached
on the template origin. Repeating the same specialization returns the same class:

.. code-block:: python

    assert Box[uint8] is Box[uint8]

Generated classes store Caterpillar-owned metadata:

``__origin__``
    The template class that produced the specialization.

``__args__``
    The concrete specialization arguments.

Because ``Box[uint8]`` returns a real class at runtime, it is not a
``typing`` generic alias after materialization. Use the metadata above instead
of ``typing.get_origin()`` and ``typing.get_args()`` for runtime inspection.

Partial Generic Templates
-------------------------

If a specialization still contains unresolved type variables, Caterpillar keeps
the result as a template.

.. code-block:: python

    from typing import Generic, TypeVar

    from caterpillar.py import template, uint8, uint16

    T = TypeVar("T")
    U = TypeVar("U")


    @template
    class Pair(Generic[T, U]):
        left: T
        right: U


    BytePair = Pair[uint8, U]
    ByteWordPair = BytePair[uint16]

``BytePair`` is a template. ``ByteWordPair`` is a concrete struct class.

Legacy Template Variables
-------------------------

Legacy templates use :class:`~caterpillar.model.TemplateTypeVar` or string
names in the decorator.

.. code-block:: python

    from caterpillar.py import TemplateTypeVar, derive, template, uint8, uint16

    A = TemplateTypeVar("A")


    @template(A, "B")
    class FormatTemplate:
        foo: A
        bar: B


    Format = derive(FormatTemplate, uint8, uint16)

Legacy templates classify parameters as required or keyword-only defaults:

* Required parameters are passed positionally or by keyword to
  :func:`~caterpillar.model.derive`.
* Keyword defaults are declared in ``@template(T=uint8)`` and may be omitted
  from ``derive()``.

The legacy decorator temporarily injects missing template names into the caller
module while annotations are evaluated. This keeps legacy templates compatible
with deferred annotation evaluation.

``derive()``
------------

``derive()`` remains available for both template systems.

For legacy templates, ``derive()`` is the primary specialization API. For
generic templates, direct subscript syntax is preferred, but ``derive()`` can be
used when a name or union option must be supplied explicitly.

.. code-block:: python

    NamedByteBox = derive(Box, uint8, name="NamedByteBox")

Passing an already materialized struct class to ``derive()`` without additional
arguments returns that class unchanged.

Type Checking
-------------

Static type checkers see generic templates as ordinary Python generic classes.
At runtime, Caterpillar replaces template arguments with concrete binary
layouts. If a project needs precise static typing for field atoms such as
``uint8``, expose typing-only aliases to their Python value types while keeping
the runtime field objects unchanged.

.. admonition:: Developer's note

    Template specialization is performed once when a concrete class is created.
    Pack and unpack operations use the normal ``Struct`` and ``Field`` paths.
