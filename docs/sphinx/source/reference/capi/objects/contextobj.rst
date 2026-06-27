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


.. c:function:: PyObject *CpContext_New(void)

    Creates a new context and returns it. Returns *NULL* if an error occurs.


.. c:function:: PyObject *CpContext_GetDict(PyObject *context)

    Returns a new reference to the dictionary backing ``context``. A native
    context is implemented as a dictionary object with additional protocol
    helpers.


.. c:function:: PyObject *CpContext_GetRoot(PyObject *context)

    Returns a new reference to ``context["_root"]`` when present; otherwise
    returns a new reference to ``context`` itself.


.. c:function:: PyObject *CpContext_GenericGetAttr(PyObject *context, PyObject *path)

    Resolves a dotted context path. The first path node is read from the context
    mapping when possible, then remaining nodes are resolved with normal Python
    attribute access. Returns a new reference or ``NULL`` on error.


.. c:function:: PyObject *CpContext_GenericGetAttrString(PyObject *context, const char *path)

    String variant of :c:func:`CpContext_GenericGetAttr`.


.. c:function:: int CpContext_GenericSetAttr(PyObject *context, PyObject *path, PyObject *value)

    Sets a context path. Single-node paths are written into the context mapping.
    Dotted paths resolve the parent path first and then assign the final
    attribute on the resolved object. Returns ``0`` on success and ``-1`` on
    failure.


.. c:function:: int CpContext_GenericSetAttrString(PyObject *context, const char *path, PyObject *value)

    String variant of :c:func:`CpContext_GenericSetAttr`.
4