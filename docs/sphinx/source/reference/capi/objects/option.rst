.. _reference-capi_option:

**************
Option Objects
**************

.. c:var:: PyTypeObject CpOption_Type

    The type object for the :c:type:`CpOptionObject` class.


.. c:type:: CpOptionObject

    Simple option struct that stores a name and a value.


.. c:function:: int CpOption_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpOptionObject`.


.. c:function:: int CpOption_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpOptionObject`