.. _tutorial-advanced-conditionals:

Conditional Fields
==================

*Conditional fields* allow a struct layout to include or skip fields based on
values that are already available in the parse context. They are useful for
versioned formats, tagged unions, optional trailer data, and protocol flags.

Python 3.14 changed when class annotations become visible during class-body
execution. Because of that, Caterpillar supports two conditional styles:

- Python <= 3.13 can use the older implicit ``with`` syntax.
- Python >= 3.14 should use explicit conditional metadata. The
  ``f[..., when]`` and ``Start(when)`` / ``End(when)`` forms are accepted by
  static type checkers because the condition markers live in ``Annotated``
  metadata.

For one field, the compact explicit form is to bind the condition with
``with If(condition) as when:`` and add ``when`` to the field metadata.

.. code-block:: python
    :caption: Compact conditional field

    @struct
    class Packet:
        flag: f[int, uint8]

        with If(this.flag == 1) as when:
            value: f[int, uint8, when]

        trailer: f[int, uint8]

When ``flag`` is not ``1``, ``value`` consumes no bytes and unpacks as ``None``.
When packing, disabled fields write no bytes.

``value: when[f[int, uint8]]`` spelling is also supported, but some
static type checkers reject it because ``when`` is a runtime value. Prefer
``f[..., when]`` for new code.

Python 3.14+ Changes
--------------------

Python3.14+ support introduces inline markers make a complete ``with`` block
conditional without adding extra class fields. Add ``Start(when)`` to the first
real field and ``End(when)`` to the last real field.

.. code-block:: python
    :caption: Type-checker-friendly inline marker block

    @struct
    class Packet:
        flag: f[int, uint8]

        with If(this.flag == 1) as when:
            first: f[int, uint8, Start(when)]
            second: f[int, uint16]
            third: f[int, uint8, End(when)]

        trailer: f[int, uint8]

When ``flag`` is not ``1``, all three fields consume no bytes and unpack as
``None``. The ``when`` alias is removed from the final struct class.

Invisible marker-field spelling is also available:

.. code-block:: python
    :caption: Compatibility marker fields

    @struct
    class Packet:
        flag: f[int, uint8]

        with If(this.flag == 1) as when:
            _: f[None, when] = Invisible()
            value: f[int, uint8]
            _end: f[None, End(when)] = Invisible()

        trailer: f[int, uint8]

Marker blocks follow these rules:

- Every ``Start(when)`` block must end with ``End(when)``.
- ``End`` must close the currently active marker.
- Use a unique alias for each Python 3.14 marker block.
- A marker block must contain at least one real field.
- Do not define the same field name in multiple marker branches. Use
  :class:`~caterpillar.fields.Branch` for same-field conditional variants.

Multiple Branches
-----------------

Use ``ElseIf(previous, condition)`` and ``Else(previous)`` to build explicit
branch chains on Python 3.14+. Each branch receives the marker returned by the
previous branch.

.. code-block:: python
    :caption: If / else-if / else marker chain

    @struct
    class Packet:
        tag: f[int, uint8]

        with If(this.tag == 1) as first:
            small: f[int, uint8, first]

        with ElseIf(first, this.tag == 2) as second:
            medium: f[int, uint16, second]

        with Else(second) as fallback:
            raw: f[int, uint8, fallback]

        trailer: f[int, uint8]

``ElseIf(first, condition)`` is active only when all previous branch conditions
are false and its own condition is true. ``Else(second)`` is active only when all
previous branch conditions are false. ``ElseIf`` cannot be added after ``Else``.

Same-Field Branches
-------------------

When multiple conditions should populate the same attribute, use ``Branch`` with
``When`` and optional ``Otherwise`` arms. This is the right spelling for tagged
fields whose binary type changes with a discriminator.

.. code-block:: python
    :caption: Same attribute, different field types

    @struct
    class Packet:
        tag: f[int, uint8]
        value: f[
            int,
            Branch(
                When(this.tag == 1, uint8),
                When(this.tag == 2, uint16),
                Otherwise(uint8),
            ),
        ]
        trailer: f[int, uint8]

Branch arms can carry normal field options by using ``f[...]`` inside the arm:

.. code-block:: python
    :caption: Branch arm with local options

    @struct(order=LittleEndian)
    class Packet:
        tag: f[int, uint8]
        value: f[
            int,
            Branch(
                When(this.tag == 1, f[int, uint16, BigEndian]),
                Otherwise(uint16),
            ),
        ]

In this example, ``value`` is big-endian only when ``tag == 1``. The fallback arm
uses the struct's surrounding byte order.

Legacy Syntax on Python <= 3.13
-------------------------------

Before Python 3.14, Caterpillar can still use the implicit class-body syntax.

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python

            @struct
            class Format:
                version: uint32

                with this.version == 1:
                    length: uint8
                    data: Bytes(this.length)

                with ElseIf(this.version == 2):
                    name: CString(16)

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python

            @struct
            class Format:
                version: uint32_t

                with this.version == 1:
                    length: uint8_t
                    data: f[bytes, Bytes(this.length)]

                with ElseIf(this.version == 2):
                    name: f[str, CString(16)]

On Python 3.14+, implicit ``with If(condition):``, ``with ElseIf(condition):``,
and ``with Else:`` blocks raise a clear exception. Use the explicit marker
syntax shown above.
