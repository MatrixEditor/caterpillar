.. _reference-capi_layer:

*************
Layer Objects
*************

.. c:var:: PyTypeObject CpLayer_Type

    The type object for the :c:type:`CpLayerObject` class.


.. c:type:: CpLayerObject

    *TODO*


.. c:function:: int CpLayer_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpLayerObject`.


.. c:function:: int CpLayer_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpLayerObject`


.. c:function:: CpLayerObject *CpLayer_New(CpStateObject* state, CpLayerObject* parent);

    Creates a new layer and returns it. Returns *NULL* if an error occurs.


.. c:function:: int CpLayer_Invalidate(CpLayerObject *layer)

    Invalidates the layer. Returns :code:`0` if successful and :code:`-1` if an
    error occurs. This function will decrease the reference count of the layer.


.. c:function:: int CpLayer_SetSequence(CpLayerObject *layer, PyObject *sequence, Py_ssize_t length, int8_t greedy)

    Sets the sequence of the layer. Returns :code:`0` if successful and :code:`-1`
    if an error occurs.


.. c:function:: void CpLayer_AppendPath(CpLayerObject *layer, PyObject *path)

    Appends the path to the layer. (macro)