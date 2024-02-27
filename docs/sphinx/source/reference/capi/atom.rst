.. highlight:: c

.. _reference-capi_atom:

Atom Protocol
=============

Caterpillar provides a special protocol for working with atoms. It is
designed to incorporate packing and unpacking of data streams as well
as calculating its size and measuring its type.


.. c:function:: int CpAtomType_CanPack(PyObject* o)
                int CpAtomType_FastCanPack(PyObject* o, _coremodulestate* state)

    Return ``1`` if the object provides an interface of packing other
    objects and ``0`` otherwise. Note that it returns ``1`` for classes
    with a :meth:`~object.__pack__` method, since the type of objects to
    be packed can not be determined by introspection.


.. c:function:: int CpAtomType_CanUnpack(PyObject* o)
                int CpAtomType_FastCanUnpack(PyObject* o, _coremodulestate* state)

    Return ``1`` if the object provides an interface of unpacking other
    objects and ``0`` otherwise. Note that it returns ``1`` for classes
    with a :meth:`~object.__unpack__` method, since the type of objects
    to be unpacked can not be determined by introspection.


.. c:function:: int CpAtomType_HasType(PyObject* o)
                int CpAtomType_FastHasType(PyObject* o, _coremodulestate* state)

    Returns ``1`` if the object provides a method of determining the type
    this object (usually an atom) represents and ``0`` otherwise. As all
    other functions, this one will simply check for the presence of the
    :meth:`~object.__type__` method.


.. c:function:: int CpAtomType_HasSize(PyObject* o)
                int CpAtomType_FastHasSize(PyObject* o, _coremodulestate* state)

    Searches for :meth:`~object.__size__`, returns ``1`` if it is
    present and ``0`` otherwise.

.. note::
    For each function introduced above, there is an alternative (faster)
    implementation that won't create a Python unicode object before calling
    :code:`getattr`. So, if a reference :c:type:`_codemodulestate` is owned,
    it's string cache will be used.


.. c:function:: PyObject *CpAtom_CallPack(PyObject* self, PyObject* name, PyObject* o, PyObject* ctx)

    Packs the object :code:`o` using context :code:`ctx` and returns the result. The
    :code:`name` describes the target method name to be called on the object :code:`self`.
    This method will return *NULL* if an error occurs while calling the target method. Proper
    use would be together with the global module state:

    .. code-block:: c

        _coremodulestate* state = _getstate();
        PyObject *o = ..., *ctx = ...;

        // invoke __pack__ manually
        PyObject* result = CpAtom_CallPack(self, state->str___pack__, o, ctx);
        if (!result) {
            return NULL;
        }
        // do something with result

    The provided context object must support the *Context Protocol*, which is not validated in
    this method. Furthermore, it must be an instance of the :c:type:`CpState` structure if the
    native *pack* function is called.

