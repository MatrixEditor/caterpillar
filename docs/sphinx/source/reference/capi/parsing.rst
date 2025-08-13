.. _reference-capi_parsing:

**********************
Packing and Unpacking
**********************


.. c:function:: PyObject *CpAtom_TypeOf(PyObject *value)

    Returns the type of the given atom object.


.. c:function:: int CpAtom_Pack(PyObject* pAtom, PyObject* pObj, PyObject *pContext)

    Packs the object :code:`o` using the provided context and returns ``-1`` on
    error. The  Proper use would be:

    .. code-block:: c

        PyObject *nAtom = ..., *nContext = ..., *nValue = ...;
        if (CpAtom_Pack(nAtom, nValue, nContext) < 0)
            goto error;

    The provided context object must support the *Context Protocol*, which is
    not validated in this method.This function may raise *NotImplementedError*
    to indicate that this class does not support packing.

    .. versionadded:: 2.6.0


.. c:function:: PyObject *CpAtom_Size(PyObject* pAtom, PyObject* pContext)

    Calculates the size of the object :code:`pAtom` using context
    :code:`pContext` and returns the result. This method will return *NULL* if
    an error occurs while calling the target function.

    .. versionadded:: 2.6.0


*TODO*
