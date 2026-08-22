.. _tutorial-dyn_byteorder:

Dynamic Byte Order
==================

In addition to traditional byte order types, *caterpillar* supports a dynamic byte order
based on the current pack or unpack context.

.. versionadded:: 2.6.4
    This feature is available in starting from version ``2.6.4``

.. versionadded:: 2.10.0
    Added the ``Inherit`` byteorder type.

There are various use-cases that require a struct to handle both big-endian and
little-endian. In order to reduce the amount of code for these structs, *caterpillar*
introduces a special byte order type: :class:`~caterpillar.byteorder.DynByteOrder`. It
supports two different configuration levels:

1. global: endianess is configured when calling :func:`~caterpillar.model.pack` or
   :func:`~caterpillar.model.unpack`.
2. struct-level: byte order is applied per struct (handed down to all fields)
3. field-level: byte order is applied per field

Each of these configuration levels support various methods of selecting the target endian:

* global configuration using an additional keyword argument in :func:`~caterpillar.model.pack` or
  :func:`~caterpillar.model.unpack`.
* context-key: configuration based on a value within the current context
* custom function: endian is derived from a custom function

Example: struct-wide dynamic byte order
---------------------------------------

Let's consider the following struct definition. The dynamic endian configuration will be applied
to all fields that haven't got an endian already set.

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :linenos:

            @struct(order=Dynamic)
            class Format:
                a: uint16           # litte endian or big endian is decided using
                b: uint32           # a global context variable

            obj = Format(a=0x1234, b=0x56789ABC)

            # pack the object using BigEndian
            pack(obj, order=BigEndian)

            # now pack with little endian
            pack(obj, order=LittleEndian)

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :linenos:

            @struct(order=Dynamic)
            class Format:
                a: uint16_t         # litte endian or big endian is decided using
                b: uint32_t         # a global context variable

            obj = Format(a=0x1234, b=0x56789ABC)

            # pack the object using BigEndian
            pack(obj, order=BigEndian)

            # now pack with little endian
            pack(obj, order=LittleEndian)

Here we pass an additional global context variable named :attr:`~caterpillar.context.CTX_ORDER` (``"_order"``)
to the packing and unpacking process. The dynamic endian will automatically infer the order based on this
global variable.

Example: field-level dynamic byte order
---------------------------------------

The same concept as shown above can be applied to single fields too. By default, the endian to use must be
given as a global context variable as described before.

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :linenos:

            @struct(order=LittleEndian)
            class Format:
                a: uint16
                b: Dynamic + uint32   # only this field will be affected

            # packing and unpacking is the same as in the previous example

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :linenos:

            @struct(order=LittleEndian)
            class Format:
                a: uint16_t
                b: f[int, Dynamic + uint32]   # only this field will be affected

            # packing and unpacking is the same as in the previous example

Example: context key reference
------------------------------

Sometimes format specifications use a special field indicating whether all following
fields are using big or little endian. To implement this kind of endian selection, a
so called *context key* can be specified, which can take one of the following forms:

*   direct reference: just a string reference

    .. tab-set::
        :sync-group: syntax

        .. tab-item:: Default Syntax
            :sync: default

            .. code-block:: python

                # ...
                spec: uint8
                number: Dynamic(key="spec") + uint32
                # ...

        .. tab-item:: Extended Syntax (>=2.8.0)
            :sync: extended

            .. code-block:: python

                # ...
                spec: uint8_t
                number: f[int, Dynamic(key="spec") + uint32]
                # ...

*   context-lambda: a function that takes the current context as its first parameter and
    returns the target endian configuration value.

    .. tab-set::
        :sync-group: syntax

        .. tab-item:: Default Syntax
            :sync: default

            .. code-block:: python

                # ...
                spec: uint8
                number: Dynamic(key=this.spec) + uint32
                # ...

        .. tab-item:: Extended Syntax (>=2.8.0)
            :sync: extended

            .. code-block:: python

                # ...
                spec: uint8
                number: f[int, Dynamic(key=this.spec) + uint32]
                # ...


The target endianess is decided based on the context value:

* :code:`str` will be applied directly as the format character
* any object storing a :code:`ch` string value
* any other object is converted to a :code:`bool` and the following mapping is applied:

  * :code:`True`: :attr:`~caterpillar.byteorder.LittleEndian`
  * :code:`False`: :attr:`~caterpillar.byteorder.BigEndian`

As an example, consider the following definition:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :linenos:

            @struct(order=BigEndian)
            class Format:
                spec: uint8 = 0
                a: DynByteOrder(key=this.spec) + uint16
                # alternatively
                # a: Dynamic(this.spec) + uint16
                b: uint32

            # packing and unpacking does not require the extra endian value
            obj = Format(spec=0, a=0x1234, b=0x56789ABC)
            # 0 -> False, results in BigEndian
            data_be = pack(obj)

            # 1 -> True, results in LittleEndian
            obj.spec = 1
            data_le = pack(obj)

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :linenos:

            @struct(order=BigEndian)
            class Format:
                spec: uint8_t = 0
                a: f[int, DynByteOrder(key=this.spec) + uint16]
                # alternatively
                # a: f[int, uint16, Dynamic(this.spec)]
                b: uint32_t

            # packing and unpacking does not require the extra endian value
            obj = Format(spec=0, a=0x1234, b=0x56789ABC)
            # 0 -> False, results in BigEndian
            data_be = pack(obj)

            # 1 -> True, results in LittleEndian
            obj.spec = 1
            data_le = pack(obj)


Example: byte order selected by an ancestor
--------------------------------------------

A nested model can select its byte order from an enclosing model by chaining
the :data:`~caterpillar.context.parent` context path. In this example,
``Inner`` is nested through ``Middle``, so
``parent.parent.byte_order`` resolves ``Outer.byte_order``:

.. code-block:: python
    :linenos:

    @struct(order=Dynamic(parent.parent.byte_order))
    class Inner:
        value: uint32

    @struct
    class Middle:
        inner: Inner

    @struct
    class Outer:
        byte_order: uint8  # 0 selects BigEndian; 1 selects LittleEndian
        middle: Middle

When unpacking, declare ``byte_order`` before ``middle`` so its value is
available when ``Inner`` resolves its dynamic byte order.

Inheriting the enclosing struct's byte order
---------------------------------------------

.. versionadded:: 2.10.0

A struct that is reused in multiple places (e.g. a shared header or record
type) sometimes needs to be decoded using whatever byte order the *embedding*
struct declares, rather than a byte order fixed at its own definition site.
The global :data:`~caterpillar.byteorder.Inherit` enables exactly this:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python
            :linenos:

            @struct(order=Inherit)
            class Inner:
                value: uint32

            @struct(order=BigEndian)
            class Outer:
                inner: Inner  # value decoded using BigEndian

            @struct(order=LittleEndian)
            class Format:
                inner: Inner  # value decoded using LittleEndian

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python
            :linenos:

            @struct(order=Inherit)
            class Inner:
                value: uint32_t

            @struct(order=BigEndian)
            class Outer:
                inner: Inner  # value decoded using BigEndian

            @struct(order=LittleEndian)
            class Format:
                inner: Inner  # value decoded using LittleEndian

A struct declared with ``order=Inherit`` resolves its byte order from the
field that embeds it, at any nesting depth (including arrays and chains of
``Inherit`` structs). If there is no enclosing struct - e.g. the struct is
used standalone or passed directly to :func:`~caterpillar.model.pack` /
:func:`~caterpillar.model.unpack` - it falls back to the regular default
byte order, exactly like a struct declared with ``order=None``.

Wrappers can use an independently ordered metadata field without changing the
order inherited by their payload. For example, this frame has a little-endian
length prefix but a big-endian inner value:

.. code-block:: python
    :linenos:

    @struct(order=BigEndian)
    class Outer:
        inner: Prefixed(LittleEndian + uint16, Inner)

``inner.value`` is decoded using ``BigEndian``; the explicit
``LittleEndian`` applies only to the prefix.

To override the byte order for a single embedding site instead of changing
``Inner`` itself, combine ``order=Inherit`` with the ``ByteOrder + Struct``
operator, mirroring the existing per-field ``ByteOrder + <atom>`` syntax:

.. code-block:: python
    :linenos:

    @struct
    class Format:
        inner: LittleEndian + Inner  # value decoded using LittleEndian

This also lets sibling fields referencing the same ``Inherit``-enabled struct
type resolve to different byte orders independently of one another - including
a plain (non-overridden) reference that keeps inheriting from the enclosing
struct alongside two explicitly-pinned siblings:

.. code-block:: python
    :linenos:

    @struct(order=BigEndian)
    class Format:
        little: LittleEndian + Inner  # always little
        big: BigEndian + Inner        # always big
        inherited: Inner              # follows Format's BigEndian

Changing ``Format``'s own order (e.g. to ``LittleEndian``) only affects the
``inherited`` field; ``little`` and ``big`` stay pinned to their explicit
override since they no longer carry ``Inherit`` at that embedding site.

As with :data:`~caterpillar.byteorder.Dynamic`, this can be composed with the
extended annotation syntax, e.g.
``f[Inner, Inner, LittleEndian]``.

.. note::
    This feature is unrelated to the struct *class* inheritance described in
    :ref:`datamodel_standard_struct` (subclassing a ``@struct``-decorated class via
    normal Python MRO). ``order=Inherit`` is about how a struct picks its byte
    order when it is *embedded as a field* in another struct, regardless of
    whether either struct participates in Python class inheritance at all.

Nesting depth and mixed byte orders
------------------------------------

``order=Inherit`` resolves through arbitrarily deep nesting, and struct chains
may freely mix explicit byte orders with ``Inherit`` at different levels. Each
``Inherit`` struct resolves against the **nearest enclosing struct that has a
concrete (non-``Inherit``) byte order** - not necessarily its immediate parent
and not necessarily the outermost struct:

.. code-block:: python
    :linenos:

    @struct(order=Inherit)
    class Inner:
        value: uint32

    @struct(order=LittleEndian)  # concrete order - breaks the chain here
    class Middle:
        inner: Inner

    @struct(order=BigEndian)
    class Outer:
        middle: Middle

    # Inner.value is decoded using Middle's LittleEndian, not Outer's
    # BigEndian, because Middle already provides
    # a concrete order for anything it embeds.

This also means a chain of several ``Inherit`` structs in a row correctly
propagates the *first* concrete order found further up the chain, however deep:

.. code-block:: python
    :linenos:

    @struct(order=Inherit)
    class Inner:
        value: uint32

    @struct(order=Inherit)
    class Middle:
        inner: Inner

    @struct(order=Inherit)
    class Outer:
        middle: Middle

    @struct(order=BigEndian)
    class Format:
        outer: Outer

    # Format.outer.middle.inner.value is decoded using BigEndian, propagated
    # through two intermediate Inherit levels.

The same resolution rule applies uniformly regardless of *how* a struct is
nested, which has been verified for:

* **Arrays**, including arrays nested inside other ``Inherit`` structs
  (``items: Inner[2]``, or an array of a struct that itself contains an
  array of ``Inherit`` structs).
* :func:`~caterpillar.model.bitfield`, which supports ``order=Inherit`` the
  same way regular structs do, whether used as a scalar member, an array
  member, or nested multiple levels deep.
* :class:`~caterpillar.py.Prefixed`, since it delegates directly to the
  wrapped struct using the same context rather than introducing its own
  field wrapper.
* :ref:`tutorial-union` structs, both as a container holding an
  ``Inherit``-enabled member and as the ``Inherit``-enabled struct itself.
