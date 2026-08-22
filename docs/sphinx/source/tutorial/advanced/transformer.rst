.. _tutorial-transformer:

Transformer
===========

Sometimes the most convenient Python-facing representation of a value isn't the same as
its representation on the wire. A percentage might be stored as a single scaled byte, or
a MAC address as six raw bytes instead of a colon-separated string. Rather than writing a
brand-new struct class from scratch every time this happens, wrap an *existing* one with
:class:`~caterpillar.fields.Transformer` and only describe the translation between the two
representations.

Several built-in structs are themselves just :class:`~caterpillar.fields.Transformer`
subclasses: :class:`~caterpillar.py.Const` (enforces a constant value),
:class:`~caterpillar.py.Enum` (maps between raw values and Python enum members),
:code:`ZLibCompressed` and derivates (compress/decompress a nested struct), and
:class:`~caterpillar.py.MACAddress` (formats six raw bytes as a colon-separated string).

A basic example
----------------

Suppose a byte should be exposed as a floating-point ratio between :code:`0.0` and
:code:`1.0` instead of a raw :code:`0`-:code:`255` integer. Subclass
:class:`~caterpillar.fields.Transformer`, wrap the underlying :code:`uint8` field, and
override :meth:`~caterpillar.fields.Transformer.encode` and
:meth:`~caterpillar.fields.Transformer.decode`:

.. code-block:: python
    :caption: A custom Transformer scaling a byte to a ratio

    # generic typing parameters read as [IN, IN_TRANSFORMED, OUT, OUT_TRANSFORMED]
    class Percentage(Transformer[float, int, float, int]):
        def __init__(self) -> None:
            super().__init__(uint8)

        def encode(self, obj: float, context) -> int:
            return round(obj * 255)

        def decode(self, parsed: int, context) -> float:
            return parsed / 255

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python

            @struct
            class Progress:
                percent: Percentage()

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python

            @struct
            class Progress:
                percent: f[float, Percentage()]

Unpacking calls the wrapped :code:`uint8` field first, then :code:`decode` on its result;
packing does the reverse, calling :code:`encode` first and feeding its result to the
wrapped field's :code:`__pack__`:

>>> unpack(Progress, b"\x80")
Progress(percent=0.5019607843137255)
>>> pack(Progress(percent=0.5))
b'\x80'

Typing
------

:class:`~caterpillar.fields.Transformer` is generic over four type parameters, describing
the two representations on either side of the translation:

.. code-block:: python

    class Transformer(Generic[_IT, _IT_transformed, _OT, _OT_transformed], FieldStruct[_IT, _OT]):
        ...

- :code:`_IT` - the type accepted from user code when *packing* (the argument to
  :code:`encode`).
- :code:`_IT_transformed` - the type produced by :code:`encode`, i.e. what the wrapped
  struct expects to pack.
- :code:`_OT_transformed` - the type produced by the wrapped struct when *unpacking*,
  i.e. the argument to :code:`decode`.
- :code:`_OT` - the type produced by :code:`decode`, i.e. the type user code ultimately
  sees.

For :code:`Percentage` above, both directions share the same pair of types - :code:`float`
on the Python side, :code:`int` on the wire - so it is declared as
:code:`Transformer[float, int, float, int]`.

For the full API, see :class:`~caterpillar.fields.Transformer` in the library reference.
