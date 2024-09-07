.. _capi_context-path:

Context Path Objects
====================

.. c:var:: PyTypeObject CpContextPath_Type

    The type object for the :c:type:`CpContextPathObject` class.


.. c:type:: CpContextPathObject

    Represents a lambda function for retrieving a value from a Context based on
    a specified path.


.. c:function:: CpContextPathObject *CpContextPath_New(PyObject* path)

    Creates a new context path and returns it. Returns *NULL* if an error occurs.


.. c:function:: CpContextPathObject *CpContextPath_FromString(const char *path)

    Creates a new context path and returns it. Returns *NULL* if an error occurs.


.. c:function:: int CpContextPath_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpContextPathObject`.


.. c:function:: int CpContextPath_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpContextPathObject`