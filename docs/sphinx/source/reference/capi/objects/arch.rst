.. _capi_arch:

Arch & Endian Objects
=====================

Arch Objects
------------

.. c:var:: PyTypeObject CpArch_Type

    The type object for the :c:type:`CpArchObject` class.


.. c:type:: CpArchObject

    *TODO*


.. c:function:: int CpArch_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpArchObject`.


.. c:function:: int CpArch_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpArchObject`.


Endian Objects
--------------

.. c:var:: PyTypeObject CpEndian_Type

    The type object for the :c:type:`CpEndianObject` class.


.. c:type:: CpEndianObject

    *TODO*

.. c:function:: int CpEndian_IsLittleEndian(CpEndianObject *endian, _modulestate *mod)

    Returns ``1`` if the current system is little-endian and ``0`` otherwise.


.. c:function:: int CpEndian_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpEndianObject`.


.. c:function:: int CpEndian_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpEndianObject`