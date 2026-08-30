.. _tutorial-basics_padding:

*******
Padding
*******

In binary file formats, padding is often used to align data to certain byte
boundaries. *Caterpillar* provides a way to handle padding within structs.
However, it is important to note that *caterpillar* doesn't store any data
associated with the padding itself unless explicitly defined. If you need
to retain or manipulate the padding content, you can use the :code:`Bytes` or
:code:`Memory` field types.

If you want to apply padding to a struct, you can simply specify the padding
length using the `padding` keyword. This is useful when you need to ensure
that certain fields are aligned or when the structure requires reserved spaces.

>>> field = padding[10] # greedy or dynamic size


.. _tutorial-align_to:

Whole-model alignment
----------------------

.. versionadded:: 2.10.0

The :code:`padding` field above reserves space explicitly, as an extra field
of its own. Sometimes what you actually want is different: a whole
:code:`@struct`, :code:`@union` or :code:`@bitfield` class whose *total*
packed size is always rounded up to a multiple of some alignment.
Pass :code:`align_to=` to the decorator instead:

>>> @struct(align_to=4)
... class Format:
...     a: uint8
...
>>> sizeof(Format)
4
>>> unpack(Format, b"\x01\x00\x00\x00")
Format(a=1)

This is deliberately different from :class:`~caterpillar.fields.Aligned` and
:func:`~caterpillar.fields.align`, which both pad relative to the *absolute*
stream position. :code:`align_to=` instead measures *this model's own* start
and end, so the padding only ever depends on the model's own content - not on
where it happens to be embedded:

>>> @struct
... class Outer:
...     b: uint8
...     inner: Format
...     c: uint8
...
>>> pack(Outer(b=1, inner=Format(a=2), c=3))
b'\x01\x02\x00\x00\x00\x03'

A bare :code:`int` or context lambda is accepted directly, as shown above.
Use :class:`~caterpillar.fields.AlignTo` explicitly to customize the fill
byte (or a multi-byte fill pattern) and/or relax verification:

>>> @struct(align_to=AlignTo(4, fill=0xFF, strict=False))
... class Lenient:
...     a: uint8

With the default :code:`strict=True`, unpacking verifies that the padding
bytes actually match :code:`fill` and raises :code:`ValueError` if they
don't. With :code:`strict=False`, padding bytes are consumed without
verification.

:code:`align_to=` also works on :code:`@union` (padding after the largest
member) and :code:`@bitfield` (padding after all bit-groups have been
finalized to whole bytes), and applies per-element when the model is used
inside an array, so each element keeps its own alignment:

>>> @struct
... class Many:
...     items: Format[2]
...
>>> pack(Many(items=[Format(a=1), Format(a=2)]))
b'\x01\x00\x00\x00\x02\x00\x00\x00'

A dynamic (context-dependent) alignment value is supported too, but makes the
model's size undeterminable ahead of time - :func:`~caterpillar.model.sizeof`
raises :class:`~caterpillar.exception.DynamicSizeError` in that case.

