.. _dev-roadmap:

********
Roadmap
********

.. |check_| raw:: html

    <input checked=""  disabled="" type="checkbox">

.. |uncheck_| raw:: html

    <input disabled="" type="checkbox">

.. role:: text-danger

.. role:: text-warning

Python API
----------

- |check_| Implementation of parsing process (unpack, pack)
- |check_| Struct class (:class:`Struct`) with wrapper function (:code:`@struct`)
- |uncheck_| Python docs and examples
- |uncheck_| Python tests

C API
-----

- |check_| Implementation of parsing process (unpack, pack)
- |uncheck_| Struct class (:c:type:`CpStructObject`)
- |uncheck_| Struct wrapper function
- |uncheck_| Python docs

Atom Objects:
^^^^^^^^^^^^^

- |check_| Integer (uint8-128 and int8-128) (C type: :c:type:`CpIntAtomObject`, Py type: :class:`int_t`)
    [:text-danger:`missing docs`]

- |check_| Float, Double (C type: :c:type:`CpFloatAtomObject`, Py type: :class:`float_t`)
    [:text-danger:`missing docs`]

- |check_| Boolean (C type: :c:type:`CpBoolAtomObject`, Py type: :class:`bool_t`)
    Global instance: :code:`boolean`,
    [:text-danger:`missing docs`]

- |check_| Char (C type: :c:type:`CpCharAtomObject`, Py type: :class:`char_t`)
    Global instance: :code:`char`,
    [:text-danger:`missing docs`]

- |check_| Padding (C type: :c:type:`CpPaddingAtomObject`, Py type: :class:`padding_t`)
    Global instance: :code:`padding`,
    [:text-danger:`missing docs`]

- |uncheck_| Bytes

- |check_| String (C type: :c:type:`CpStringAtomObject`, Py type: :class:`string`)
    [:text-danger:`missing docs`],
    [:text-warning:`missing perftest`]

- |check_| Const (C type: :c:type:`CpConstAtomObject`, Py type: :class:`const_t`)
    [:text-danger:`missing docs`],
    [:text-warning:`missing perftest`]

- |uncheck_| CString
- |check_| Bytes (C type: :c:type:`CpBytesAtomObject`, Py type: :class:`octetstring`)
    [:text-danger:`missing docs`],
    [:text-warning:`missing perftest`]

- |check_| Enum (C type: :c:type:`CpEnumAtomObject`, Py type: :class:`enumeration`)
    [:text-danger:`missing docs`],
    [:text-warning:`missing perftest`]

- |check_| Computed (C type: :c:type:`CpComputedAtomObject`, Py type: :class:`computed`)
    [:text-danger:`missing docs`],
    [:text-warning:`missing perftest`]

- |check_| PString (C type: :c:type:`CpPStringAtomObject`, Py type: :class:`pstring`)
    [:text-danger:`missing docs`],
    [:text-warning:`missing perftest`]

- |uncheck_| Prefixed
    [:text-danger:`create issue (discuss relevance)`]

- |check_| Lazy
    [:text-danger:`missing docs`],
    [:text-warning:`missing perftest`]

- |uncheck_| uuid
- |uncheck_| Conditional: If, Else, ElseIf
- |check_| VarInt (C type: :c:type:`CpVarIntAtomObject`, Py type: :class:`varint_t`)
    [:text-danger:`missing docs`],
    [:text-warning:`missing perftest`]

- |uncheck_| While