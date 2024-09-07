.. _reference-capi_field:

*************
Field Objects
*************

.. c:var:: PyTypeObject CpField_Type

    The type object for the :c:type:`CpFieldObject` class.


.. c:type:: CpFieldObject

    C implementation of the Python equivalent. Represents a field in a data structure.


.. c:function:: int CpField_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpFieldObject`.


.. c:function:: int CpField_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpFieldObject`


.. c:function:: CpFieldObject *CpField_New(PyObject *atom)

    Creates a new field and returns it. Returns *NULL* if an error occurs.


.. c:function:: int CpField_HasCondition(CpFieldObject *field)

    Returns whether the field has a condition. This function always succeeds.


.. c:function:: int CpField_IsEnabled(CpFieldObject *field, PyObject *context)

    Returns whether the field is enabled. The context object must conform to
    the context protocol.Returns :code:`1` if the field is enabled, :code:`0`
    otherwise and returns :code:`-1` if an error occurs.


.. c:function:: Py_ssize_t CpField_GetOffset(CpFieldObject *field, PyObject *context)

    Returns the offset of the field. The context object must conform to the
    context protocol. Returns :code:`-1` if an error occurs.


.. c:function:: PyObject *CpField_EvalSwitch(CpFieldObject *field, PyObject *value, PyObject *context)

    Evaluates a switch field (if configured to do so). The context object must conform to the
    context protocol. Returns *NULL* if an error occurs.


.. c:function:: PyObject *CpField_GetLength(CpFieldObject *field, PyObject *context)

    Returns the length of the field. The context object must conform to the
    context protocol. Returns *NULL* if an error occurs.