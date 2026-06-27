.. _reference-capi_parsing:

**********************
Packing and Unpacking
**********************


.. c:function:: PyObject *CpAtom_TypeOf(PyObject *value)

    Returns a new reference containing the type reported by ``value``.
    Native atoms use their ``ob_type`` slot; other objects are called through
    ``__type__``. Returns ``NULL`` and sets an exception on failure.


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

.. c:function:: PyObject *CpAtom_Unpack(PyObject* pAtom, PyObject* pContext)

    Unpacks a value using ``pAtom`` and ``pContext``. Native atoms use their
    ``ob_unpack`` slot; Python objects are called through ``__unpack__``.
    Returns a new reference on success or ``NULL`` on failure.

    .. versionadded:: 2.6.0

.. c:function:: int CpAtom_PackMany(PyObject* pAtom, PyObject* pObj, PyObject* pContext, PyObject* pLengthInfo)

    Packs a sequence of objects using ``__pack_many__`` semantics. Returns
    ``0`` on success and ``-1`` on failure.

    .. versionadded:: 2.6.0

.. c:function:: PyObject *CpAtom_UnpackMany(PyObject* pAtom, PyObject* pContext, PyObject* pLengthInfo)

    Unpacks multiple objects using ``__unpack_many__`` semantics and returns the
    result as a new reference.

    .. versionadded:: 2.6.0


.. c:function:: PyObject *CpAtom_Size(PyObject* pAtom, PyObject* pContext)

    Calculates the size of the object :code:`pAtom` using context
    :code:`pContext` and returns the result. This method will return *NULL* if
    an error occurs while calling the target function.

    .. versionadded:: 2.6.0

.. c:function:: PyObject *CpAtom_BitsOf(PyObject* pAtom)

    Returns the bit count reported by ``pAtom``. Native atoms use their
    ``ob_bits`` slot. Python objects are resolved through ``__bits__``; if the
    attribute is callable it is called without arguments, otherwise the
    attribute value is returned as-is. Returns a new reference or ``NULL`` on
    failure.

    .. versionadded:: 2.6.0
