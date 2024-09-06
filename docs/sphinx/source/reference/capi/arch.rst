.. _capi_arch:

Arch & Endian
=============

Arch
----


Endian
------

.. c:var:: PyTypeObject CpEndian_Type

    The type object for the :c:type:`CpEndian` class.


.. c:type:: CpEndianObject

    *TODO*

.. c:function:: int CpEndian_IsLittleEndian(CpEndianObject *endian, _modulestate *mod)

    Returns ``1`` if the current system is little-endian and ``0`` otherwise.


.. c:function:: int CpEndian_CheckExact(PyObject *op)

    *TODO*


.. c:function:: int CpEndian_Check(PyObject *op)

    *TODO*