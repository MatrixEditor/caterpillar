.. _reference-capi_parsing:

**********************
Packing and Unpacking
**********************


.. c:function:: PyObject *CpTypeOf(PyObject *value)
                PyObject *CpTypeOf_Field(CpFieldObject *field)
                PyObject *CpTypeOf_Common(PyObject *op)

    Returns the type of the given atom object.

.. c:function:: PyObject *CpSizeOf(PyObject *atom, PyObject *globals)
                PyObject *CpSizeOf_Field(CpFieldObject *, CpLayerObject *)
                PyObject *CpSizeOf_Struct(CpStructObject *, CpLayerObject *)
                PyObject *CpSizeOf_Common(PyObject *, CpLayerObject *)

    Returns the size of the given atom object.

.. c:function:: int CpPack(PyObject *op, PyObject *atom, PyObject *io, PyObject *globals)

    Packs the given value using the given atom object and returns :code::`0` if
    successful. Returns :code:`-1` if an error occurs. The *globals* parameter may
    be *NULL*.

    Serializing objects follows specific rules when it comes to CpLayerObject
    creation. The first layer (root layer) will be assigned with the path
    '<root>'. By default, cp_pack will automatically create a new layer object
    when called. Therefore, it is recommended to utilize cp_pack_internal for
    C calls to avoid unnecessary layer creation.

    Currently, the following conditions allow the creation of a new layer:

    - Start packing an object
    - Serializing a sequence object that requires to iterate over all elements individually. Note that atoms that support :code:`__unpack_many__` won't be called with the newly created sequence layer.
    - Struct object or named sequences of fields in general will always introduce a new layer object.

    There are some built-in types that are designed to fasten calls by providing
    a native C implementation. It is recommended to implement new classes in C
    to leverage its speed rather than define new Python atom classes.

    A full workflow of cp_pack with all layers displayed would be the following:

    .. code-block:: text

        1. cp_pack: create new state and root layer         | l: <root>
        2. cp_pack_internal: measure atom type and call     |         <--+-+-+
           according C method                               | l: <root>  | | |
        3. One of the following methods will be called:                  | | |
          a. cp_pack_catom: calls native C method           | l: <root>  | | |
          b. cp_pack_atom: call python pack method          | l: <root>  | | |
          c. cp_pack_field: inserts the field instance into              | | |
             the current layer and calls cp_pack_internal                | | |
             again.                                         | l: <root> -+ | |
          d. cp_pack_struct: creates a new object layer                    | |
             that addresses only the current struct's                      | |
             values. Calls cp_pack_internal on each field   | l: <obj>  ---+ |
          e. cp_pack_common: createsa a new layer if                         |
             multiple objects should be packed AND                           |
             __[un]pack_many__ is not implemented.          | l: <seq|root> -+

    The following functions are defined and called within the packing process:

    .. c:function:: int CpPack_Field(PyObject *, CpFieldObject *, CpLayerObject *)
                    int CpPack_Struct(PyObject *, CpStructObject *, CpLayerObject *)
                    int CpPack_CAtom(PyObject *, CpCAtomObject *, CpLayerObject *)
                    int CpPack_Common(PyObject *, PyObject *, CpLayerObject *)
                    int _Cp_Pack(PyObject*, PyObject*, CpLayerObject* )

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

    Unlike serializing objects, unpacking returns fully qualified objects as a
    result. In addition, the internal 'obj' within a struct layer will be a
    :c:type:`CpContextObject` instance.

    The following functions are defined and called within the unpacking process:

    .. c:function:: PyObject *_Cp_Unpack(PyObject*, CpLayerObject*)
                    PyObject *CpUnpack_Field(CpFieldObject*, CpLayerObject*)
                    PyObject *CpUnpack_Struct(CpStructObject*, CpLayerObject*)
                    PyObject *CpUnpack_CAtom(CpCAtomObject*, CpLayerObject*)
                    PyObject *CpUnpack_Common(PyObject *, CpLayerObject*)
