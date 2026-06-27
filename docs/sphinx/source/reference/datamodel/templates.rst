.. _ref-templates:

Templates
=========

A specialized form of structs are *templates*, which are basically generic Python classes. Think of them
as blueprints for your final classes/structs that contain placeholders for actual types. As in C++, a
template needs type arguments, in this case we will name them :class:`~caterpillar.model.TemplateTypeVar`.

Actually, there are two different types of type variables:

* Required:
    These variables are **required** when creating a new struct based on the template and they
    can be used as positional arguments within the type derivation.

* Positional:
    These arguments are usable only as keyword arguments and are may be optional if a default value
    is supplied.

These template type variables can be created using simple variable definitions:

>>> A = TemplateTypeVar("A")

.. important::
    A template class is **not** a struct definition. It specifies a blueprint for the final class.

A template class is defined like a struct, union or bitfield class, but without being a
dataclass nor storing a struct instance.

.. code-block:: python

    >>> @template(A, "B")
    ... class FormatTemplate:
    ...     foo: A
    ...     bar: B
    ...     baz: uint32
    ...

The defined class then can be used to create new classes based on the provided class
structure. For instance,

.. code-block:: python

    >>> Format = derive(FormatTemplate, A=uint32, B=uint8)
    >>> Format
    <class '__main__.__4BE4F2562B65393CFormatTemplate'>

will return an anonymous class (in this case). Normally, *caterpillar* tries to infer the
variable name from the current module (if :code:`name=...`). In summary, every time
:meth:`~caterpillar.model.derive` is called, a new class will be created if not already
defined.

The current implementation materializes the class annotations with
``inspect.get_annotations()`` while the temporary template variables are still
available. This keeps templates compatible with Python versions that defer
annotation evaluation. Template information is then stored on the class using a
special class attribute: :attr:`~class.__template__`.

To support sub-classes of templates, derive a partial template:

.. code-block:: python

    >>> Format32 = derive(FormatTemplate, A=uint32, partial=True)

Again, the resulting class is **not** a struct, but another template class.
Provided replacements are stored in the new template metadata, while missing
required variables must still be supplied by a later non-partial
:func:`~caterpillar.model.derive` call.

The ``name`` parameter controls the generated class name. Passing ``name=...``
asks Caterpillar to infer the assignment target when possible; otherwise an
anonymous deterministic name is generated from the replacements.

.. admonition:: Developer's note

    By now, a template won't copy existing field documentation comments. Therefore, you
    can't display inherited members using sphinx.