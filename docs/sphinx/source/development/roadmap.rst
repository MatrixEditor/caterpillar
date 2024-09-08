.. _dev-roadmap:

********
Roadmap
********

.. |check_| raw:: html

    <input checked=""  disabled="" type="checkbox">

.. |uncheck_| raw:: html

    <input disabled="" type="checkbox">

.. role:: text-danger

Python API
----------

- |check_| Implementation of parsing process (unpack, pack)
- |check_| Struct class (:class:`Struct`) with wrapper function (:code:`@struct`)


C API
-----

- |check_| Implementation of parsing process (unpack, pack)
- |uncheck_| Struct class (:c:type:`CpStructObject`)
- |uncheck_| Struct wrapper function
- |uncheck_| Python docs

Atom Objects:
^^^^^^^^^^^^^

- |check_| Integer (uint8-128 and int8-128) (C type: :c:type:`CpIntAtomObject`, Py type: :class:`int_t`) [:text-danger:`missing docs`]
- |check_| Float, Double (C type: :c:type:`CpFloatAtomObject`, Py type: :class:`float_t`) [:text-danger:`missing docs`]
- |check_| Boolean (C type: :c:type:`CpBoolAtomObject`, Py type: :class:`bool_t`), global instance: :code:`boolean` [:text-danger:`missing docs`]
- |check_| Char (C type: :c:type:`CpCharAtomObject`, Py type: :class:`char_t`), global instance: :code:`char` [:text-danger:`missing docs`]
- |check_| Padding (C type: :c:type:`CpPaddingAtomObject`, Py type: :class:`padding_t`), global instance: :code:`padding` [:text-danger:`missing docs`]
- |check_| String (C type: :c:type:`CpStringAtomObject`, Py type: :class:`string`) [:text-danger:`missing docs`]
- |uncheck_| Const (C type: :c:type:`CpConstAtomObject`, Py type: :class:`const_t`) [:text-danger:`missing docs`]
- |uncheck_| CString
- |uncheck_| Bytes (C type: :c:type:`CpBytesAtomObject`, Py type: :class:`octetstring`)
- |uncheck_| Enum
- |uncheck_| Computed
- |uncheck_| PString
- |uncheck_| Prefixed
- |uncheck_| Lazy
- |uncheck_| uuid
- |uncheck_| Conditional: If, Else, ElseIf
- |uncheck_| VarInt
- |uncheck_| While