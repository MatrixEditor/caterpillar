.. _reference-capi_macros:

Defined Macros
==============



.. c:macro:: _Cp_Name(name)

    Appends the name of the C module to the given name. For example, if the given
    name is :code:`"foo"`, the returned name is :code:`"caterpillar._C.foo"`.


.. c:function:: PyObject *CpObject_Create(PyObject *type, const char *format, ...)

    Creates an object of the given type using the given arguments and returns it.
    Returns *NULL* if an error occurs.

.. c:function:: PyObject *CpObject_CreateOneArgs(PyObject *type, PyObject *arg)

    Creates an object of the given type using the given argument and returns it.
    Returns *NULL* if an error occurs.

.. c:function:: PyObject *CpObject_CreateNoArgs(PyObject *type)

    Creates an object of the given type and returns it. Returns *NULL* if an error occurs.

