.. _unnamed-reference:

Unnamed
=======

**Unnamed** provides a different take on the same C-union idea as :ref:`union-reference`:
instead of a whole struct where every field shares memory, :class:`~caterpillar.fields.Unnamed`
is a single *field* whose value may be one of several possible types, all overlaid on the
same fixed-size window of bytes. It is declared with a subscription syntax rather than a
decorator:

.. code-block:: python

    >>> @struct
    ... class Format:
    ...     value: Unnamed[uint32, CString(4)]
    ...

Unlike :func:`~caterpillar.model.union`, an :class:`~caterpillar.fields.Unnamed` value does
not eagerly decode every alternative. The fixed-size byte window is read once, immediately,
like any other field - but each alternative is only decoded (and then cached) the first time
it is actually requested, via :code:`value[i]` or the shorthand attribute form
:code:`value._i`:

.. code-block:: python

    >>> obj = unpack(Format, b"\x01\x00\x00\x00ABC\x00")
    >>> obj.value[0]
    1
    >>> obj.value._1
    'ABC'

Sizing
------

By default, the field's size is the *largest* of its member types' sizes - every member
must therefore have a statically-known, fixed :code:`__size__`. An explicit size (an
:code:`int` or a context lambda) can be supplied via :code:`.sized(...)` to override this,
which is required if any member has a greedy or otherwise unsized :code:`__size__`:

.. code-block:: python

    >>> @struct
    ... class Format:
    ...     n: uint16
    ...     value: Unnamed[uint32, uint16].sized(this.n)
    ...

Access
------

* :code:`value[i]` / :code:`value._i` - decode (or return the cached) member ``i``.
  Negative indices are supported.
* :code:`value[i:j]` - returns a plain :code:`tuple` of the decoded members in that range.
* :code:`len(value)` - the number of members.
* Iterating a value decodes and yields every member in order.

An :class:`~caterpillar.fields.Unnamed` value can also be constructed directly, without a
prior unpack - this is how you produce a value for packing from scratch:

>>> Unnamed()                  # nothing assigned yet
Unnamed()
>>> Unnamed(1, 2, 3)           # positional: fills index 0, 1, 2
Unnamed(1, 2, 3)
>>> Unnamed(_3=0xBEEF)         # keyword: only index 3 is set
Unnamed(?, ?, ?, 48879)

Positional arguments fill indices left to right starting at ``0``; keyword arguments named
``_<index>`` (e.g. ``_0``, ``_3``) set an arbitrary index directly.

For more information and examples, see :ref:`tutorial-unnamed`.
