.. _dev-roadmap:

********
Roadmap
********

.. |check_| raw:: html

    <input checked=""  disabled="" type="checkbox">

.. |uncheck_| raw:: html

    <input disabled="" type="checkbox">

C API
-----

|check_| Implementation of parsing process (unpack, pack)

|check_| Struct class (:c:type:`CpStructObject`)

|uncheck_| Struct wrapper function

Atom Objects:
^^^^^^^^^^^^^

- |check_| Integer (uint8-128 and int8-128) (C type: :c:type:`CpIntAtomObject`, Py type: :class:`int_t`)
- |check_| Float, Double (C type: :c:type:`CpFloatAtomObject`, Py type: :class:`float_t`)
- |check_| Boolean (C type: :c:type:`CpBoolAtomObject`, Py type: :class:`bool_t`), global instance: :code:`boolean`
- |check_| Char (C type: :c:type:`CpCharAtomObject`, Py type: :class:`char_t`), global instance: :code:`char`
- |check_| Padding (C type: :c:type:`CpPaddingAtomObject`, Py type: :class:`padding_t`), global instance: :code:`padding`
- |check_| String (C type: :c:type:`CpStringAtomObject`, Py type: :class:`string`)