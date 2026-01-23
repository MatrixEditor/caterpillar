.. _tutorial_pointers:

Pointers
========

In *Caterpillar*, pointers are emulated using special structs that behave according
to the underlying architecture. This feature allows you to model pointer-like behavior
in your data structures, making it easier to work with architecture-dependent data
formats. Pointers in this context refer to memory addresses, often used to reference
other data structures or objects.

To define a pointer in *Caterpillar*, you can use the :code:`*` operator in conjunction with
a field, which indicates that the field should behave like a pointer to another data
type. Here's an example:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python

            @struct
            class Format:
                name: uintptr *CString(...)      # Using multiplication to model a pointer

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python

            @struct
            class Format:
                # Using multiplication to model a pointer
                name: f[pointer[str], uintptr *CString(...)]


The behavior of a pointer depends on the architecture it is being unpacked on. For
example, on an x86 architecture, the pointer will be interpreted accordingly based
on how pointers are represented in memory for that platform.

.. code-block:: python

    >>> data = b"\x00\x00\x00\x04Hello, World!\x00"
    >>> o = unpack(Format, data, _arch=x86)
    Format(name=<str* 0x4>)
    >>> o.name.obj
    'Hello, World!'

The pointer behavior is facilitated by the :code:`pointer` class in *Caterpillar*. This
class acts as a standard integer that stores the parsed model object (the referenced
data). The pointer itself is an integer value, but it also holds a reference to the
object it points to.