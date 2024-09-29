.. _reference-capi_state:

*************
State Objects
*************

.. c:var:: PyTypeObject CpState_Type

    The type object for the :c:type:`CpStateObject` class.


.. c:type:: CpStateObject

    A special class that conforms to the Context protocol used in C
    packing and unpacking functions.

    It is meant to be a replacement to the Python `Context` class as it solves
    a few problems. For instance, there may be global variables passed to the
    `unpack` function. Instead of copying them into every parsing layer, we just
    store them in the state object. The state is meant to be accessible from any
    layer in the parsing process.


.. c:function:: int CpState_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpStateObject`.


.. c:function:: int CpState_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpStateObject`


.. c:function:: CpStateObject *CpState_New(PyObject *io)

    Creates a new state and returns it. Returns *NULL* if an error occurs.


.. c:function:: PyObject *CpState_Tell(CpStateObject *state)

    Returns the current position of the state. Returns *NULL* if an error occurs.


.. c:function:: PyObject *CpState_Seek(CpStateObject *state, Py_ssize_t pos, PyObject whence)

    Seeks to the given position. Returns :code:`0` if successful. Returns :code:`-1`
    if an error occurs.


.. c:function:: PyObject *CpState_Read(CpStateObject *state, Py_ssize_t size)

    Reads the given number of bytes. Returns *NULL* if an error occurs. This function
    will verify the amount of bytes read from the stream.


.. c:function:: PyObject *CpState_ReadFully(CpStateObject *state)

    Reads the entire stream. Returns *NULL* if an error occurs.


.. c:function:: PyObject *CpState_Write(CpStateObject *state, PyObject *bytes)

    Writes the given bytes to the stream. Returns *NULL* if an error occurs.


.. c:function:: int CpState_SetGlobals(CpStateObject *state, PyObject *globals)

    Sets the global namespace for pre-defined context variables. Returns :code:`0` if
    successful and :code:`-1` if an error occurs.