.. _datamodel_standard_bitfield:

Bit-field
=========


A *Bit-field*, despite its name suggesting a field of bits, is a powerful structure designed for
detailed byte inspection. Similar to other structures, it is a finite collection of named fields. This
section will introduce potential challenges associated with the implementation of a :class:`~caterpillar.model.Bitfield`
and explains its behavior.

.. versionchanged:: 2.5.0
    Completely reworked the internal :class:`Bitfield` behaviour, model and processing.

Concept
-------

Each Bitfield instance maintains a sequence of bitfield groups, where each group
contains a collection of sized fields. A bitfield group may consist of either multiple
entries (i.e., any types that can be converted to an integral type) or a single
:class:`_StructLike` object. For example, consider the following bitfield definition:

.. code-block:: python

  @bitfield
  class Format:
      a1: 2
      a2: 1
      _ : 0
      b1: char
      c1: uint32

This Bitfield definition will generate three distinct bitfield groups (labeled here as
groups a, b, and c). By default, bitfields use 8-bit alignment, leading to the following
layout:

.. code-block::

      Group      Pos       Bits
      a          0x00      8
      b          0x01      8
      c          0x02      32

Internally, only the first group requires special bit-level parsing. The remaining groups
(b and c) are treated as standard structures since they span full bytes or words without
sub-byte alignment. This dynamic grouping mechanism allows leveraging full struct-like
class definitions within bitfields.

Syntax
------

This new approach enables more complex and expressive bitfield definitions. The annotation
syntax is therefore extended as follows:

.. raw:: html

    <table class="t-stbl">
        <tbody>
            <tr>
                <td colspan="10" class="t-hr">
                </td>
            </tr>
            <tr>
                <td>
                    <span class="t-decl-id">name</span>
                    <code><b>:</b></code>
                    <span class="t-decl-id">bits</span>
                    <code><b>-</b></code>
                    <span class="t-decl-id">field</span>
                    <span class="t-decl-opt">(optional)</span>
                </td>
                <td class="t-no"> (1)
                </td>
                <td>
                </td>
            </tr>
            <tr>
                <td colspan="10" class="t-hr">
                </td>
            </tr>
            <tr>
                <td>
                    <span class="t-decl-id">name</span>
                    <code><b>:</b></code>
                    <code><b>0<b></code>
                </td>
                <td class="t-no"> (2)
                </td>
                <td>
                </td>
            </tr>
            <tr>
                <td colspan="10" class="t-hr">
                </td>
            </tr>
            <tr>
                <td>
                    <span class="t-decl-id">name</span>
                    <code><b>:</b></code>
                    <span class="t-decl-id">field-or-action </span>
                </td>
                <td class="t-no"> (3)
                </td>
                <td>
                </td>
            </tr>
            <tr>
                <td colspan="10" class="t-hr">
                </td>
            </tr>
            <tr>
                <td>
                    <span class="t-decl-id">name</span>
                    <code><b>:</b></code>
                    <code><b>(</b></code>
                    <span class="t-decl-id">field</span>
                    <code><b>,</b></code>
                    <span class="t-decl-id">factory</span>
                    <code><b>)</b></code>
                </td>
                <td class="t-no"> (4)
                </td>
                <td>
                </td>
            </tr>
            <tr>
                <td colspan="10" class="t-hr">
                </td>
            </tr>
                <td>
                    <span class="t-decl-id">name</span>
                    <code><b>:</b></code>
                    <code><b>(</b></code>
                    <span class="t-decl-id">bits</span>
                    <code><b>,</b></code>
                    <span class="t-decl-id">factory</span>
                    <span class="t-decl-opt">(optional)</span>
                    <code><b>,</b></code>
                    <span class="t-decl-id">options</span>
                    <span class="t-decl-opt">(optional)</span>
                    <code><b>)</b></code>
                </td>
                <td class="t-no"> (5)
                </td>
                <td>
                </td>
            </tr>
            <tr>
                <td colspan="10" class="t-hr">
                </td>
            </tr>
        </tbody>
    </table>

Each identifier named above is bound to certain constraints:

.. raw:: html

    <table class="t-par-begin">
        <tbody>
            <tr class="t-par">
                <td> <span class="t-decl-id"><i>name</i></span>
                </td>
                <td> -
                </td>
                <td> Any valid Python attribute name.
                </td>
            </tr>
            <tr class="t-par">
                <td> <span class="t-decl-id"><i>bits</i></span>
                </td>
                <td> -
                </td>
                <td> Any valid positive integer starting from <code>0</code>.
                </td>
            </tr>
            <tr class="t-par">
                <td> <span class="t-decl-id"><i>field</i></span>
                </td>
                <td> -
                </td>
                <td>
                    Any valid field definition for a struct resulting in a
                    <code class="xref py py-class docutils literal notranslate"><span class="pre">_StructLike</span></code>
                    that implements the subtract-operation resulting in a
                    <code class="xref py py-class docutils literal notranslate"><span class="pre">Field</span></code>
                    instance.
                </td>
            </tr>
            <tr class="t-par">
                <td> <span class="t-decl-id"><i>field-or-action</i></span>
                </td>
                <td> -
                </td>
                <td>
                    Any valid field definition for a struct resulting or an object implementing the
                    <code class="xref py py-class docutils literal notranslate"><span class="pre">_ActionLike</span></code>
                    protocol.
                </td>
            </tr>
            <tr class="t-par">
                <td> <span class="t-decl-id"><i>factory</i></span>
                </td>
                <td> -
                </td>
                <td>
                    Either a target Python type to use as factory or an instance of
                    <a class="reference internal" href="../library/model/bitfield.html#caterpillar.model.BitfieldValueFactory" title="caterpillar.model.BitfieldValueFactory"><code class="xref py py-class docutils literal notranslate"><span class="pre">BitfieldValueFactory</span></code></a>.
                </td>
            </tr>
            <tr class="t-par">
                <td> <span class="t-decl-id"><i>options</i></span>
                </td>
                <td> -
                </td>
                <td>
                    One or more options represented either as flags or instances of
                    <a class="reference internal" href="../library/model/bitfield.html#caterpillar.model.SetAlignment" title="caterpillar.model.SetAlignment"><code class="xref py py-class docutils literal notranslate"><span class="pre">SetAlignment</span></code></a>.
                </td>
            </tr>
        </tbody>
    </table>

What that syntax allows can be seen in the following example:

.. code-block:: python
    :caption: Bit-field definition using all syntax rules

    @bitfield
    class Format: #                                               -.
        # Any annotation that can be converted by a TypeConverter  | 1. Group
        # into as _StructLike object is allowed.                   | (3 Bytes)
        magic: b"foo" # bytes                                     -'

        # Syntax according to (1) and (2)                         -.
        version : 4 # int                                          | 2. Group
        state   : 3 # int                                          | (1 Byte / 8 Bits)
        _       : 0 # ignored/removed                             -'

        # Extended Syntax (5)
        flag1 : (1, SetAlignment(16))     # bool, new alignment   -.
        flag2 : 1                         # bool                   | 3. Group
        name  : (12, CharFactory)         # str                    | (2 Bytes / 16 Bits)
        type  : (2, SimpleEnum, EndGroup) # SimpleEnum            -'


Processing Rules
----------------

Based on the previously defined syntax, some processing constraints were derived:

- Rule 1.:
    - Default alignment is 1 byte (8 bits).
    - Zero (``0``) bits are prohibited.
    - If followed by a (2) declaration, the remaining bits in the current byte are padded.
    - If a ``<field>`` is provided:
        - typeof(``<field>``) is used to infer the factory.
        - :func:`~caterpillar.model.getbits` and :func:`~cateprillar.model.sizeof` determine the field's alignment.
    - If a custom alignment is configured in the Bitfield constructor, inferred alignment is ignored unless the field includes the :attr:`~cateprillar.options.B_OVERWRITE_ALIGNMENT` option.
    - If the :attr:`~cateprillar.options.B_GROUP_END` option is set, the current group is finalized and a new one is started.

- Rule 2.:
    - This rule forces alignment to the next byte boundary.
    - The field is ignored during final class generation (name is discarded).
    - The current group is finalized unless the bitfield is configured with :attr:`~caterpillar.options.B_GROUP_KEEP`

- Rule 3.:
    - Equivalent to struct-like class field definitions.
    - Automatically implies a rule 2 alignment.
    - Always finalizes the current group regardless of :attr:`~caterpillar.options.B_GROUP_KEEP`.

- Rule 4.:
    - Extension of (1).
    - Explicitly defines a conversion factory for the field.
    - The factory must be:
        - A built-in type (e.g., int, bool) supporting ``__int__``, or
        - A type or instance of :class:`BitfieldValueFactory`.

- Rule 5.:
    - Builds upon (4) with support for options.
    - Options can be passed as a list or single element.
    - Supported Options:
        - :attr:`~caterpillar.model.NewGroup`: Aligns the current group, starts a new one, and adds the entry to it.
        - :attr:`~caterpillar.model.EndGroup`: Adds the entry to the current group, then aligns it.
        - :class:`SetAlignment`: Changes the current working alignment.
    - Note: Option order affects behavior and must be considered carefully.
