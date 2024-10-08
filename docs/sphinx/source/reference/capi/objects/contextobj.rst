.. _capi_context-obj:

Context Objects
===============



.. c:var:: PyTypeObject CpContext_Type

    The type object for the :c:type:`CpContextObject` class.


.. c:type:: CpContextObject

    C implementation of the Python equivalent. Represents a context object
    with attribute-style access, which also conforms to the context protocol.


.. c:function:: int CpContext_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpContextObject`.


.. c:function:: int CpContext_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpContextObject`.


.. c:function:: CpContextObject *CpContext_New(void)

    Creates a new context and returns it. Returns *NULL* if an error occurs.


