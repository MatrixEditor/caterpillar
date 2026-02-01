.. _first_steps-extended-syntax:

Extended Syntax
===============

The extended syntax introduces a declarative and type-checker-friendly way to
define structs using ordinary Python classes. Instead of constructing structures
through procedural builder calls, you describe the format directly through type
annotations, decorators, and a small set of expressive field descriptors.

At the heart of this design is the idea that a structure definition should be
understandable at a glance, statically analyzable by tools such as Pyright or
MyPy, and immediately usable for packing and unpacking without auxiliary
boilerplate. A class defined with ``@struct`` or ``@bitfield`` is not merely
a container for data; it is the authoritative specification of how that data
exists in binary form.

The role of the field descriptor
--------------------------------

The generic descriptor ``f[PythonType, FieldSpec]`` is central to the extended
syntax. It decouples the Python representation of a field from the way it is
encoded in memory or on the wire.

When you write

.. code-block:: python

    value  : f[str, CString(10)]

you are declaring that the user of the class interacts with a Python ``str``, while
the underlying binary representation is a c-string occupying 10 characters. This
separation allows very expressive layouts without sacrificing clarity or type safety.

This becomes particularly powerful when fields depend on other fields:

.. code-block:: python

    length : uint8_t
    name   : f[str, String(this.length)]

Invisible Fields
----------------

An important concept introduced by the extended syntax is the :func:`Invisible` field. Some parts
of a binary layout are required for correctness but should not appear in the constructor
or the public interface of the class. Examples include magic constants, padding, alignment
helpers, and :ref:`tutorial-advanced-actions`.

By assigning such fields using Invisible(), they remain part of the layout while disappearing
from the type checker's perspective:

.. code-block:: python

    magic  : f[bytes, b"ABCDEF"] = Invisible()

This field is always present in the binary representation. It is written automatically when
packing and verified automatically when unpacking, yet it does not appear as a constructor
parameter and is ignored by type checkers when instantiating the class.