.. _reference-capi_parsing:

**********************
Packing and Unpacking
**********************


.. c:function:: PyObject *CpTypeOf(PyObject *value)
                PyObject *CpTypeOf_Field(CpFieldObject *field)
                PyObject *CpTypeOf_Common(PyObject *op)

    Returns the type of the given atom object.


.. c:function:: PyObject *CpSizeOf(PyObject *atom, PyObject *globals)

    Returns the size of the given atom object.


.. c:function:: int CpPack(PyObject *op, PyObject *atom, PyObject *io, PyObject *globals)

    Packs the given value using the given atom object and returns :code::`0` if
    successful. Returns :code:`-1` if an error occurs. The *globals* parameter may
    be *NULL*.


.. c:function:: int _CpPack_EvalLength(CpLayerObject* layer, PyObject* length, Py_ssize_t size, bool* seq_greedy, Py_ssize_t* seq_length)

        Evaluates the length of the sequence to pack.

        This funtion can be utilized to evaluate the length of the sequence to
        pack. It uses the :code:`size` parameter to validate the input sequence.
        Although, the :code:`size` parameter is not mandatory, it is recommended
        - a value of :code:`-1` will disable the check mentioned before.

        :param layer: the current layer that is marked as sequential
        :param size: the size of the input sequence to pack (might be -1, see above)
        :param seq_greedy: destination pointer to store the result whether the sequence should be parsed greedily
        :param seq_length: destination pointer to store the length of the sequence
        :return: :code:`0` if successful, :code:`-1` if an error occurs


.. c:function:: PyObject *CpUnpack(PyObject *atom, PyObject *io, PyObject *globals)

    *TODO*

