.. _reference-capi_struct:

**************
Struct Objects
**************

As described in the Python reference, a *struct* describes a finite collection of
named and *unnamed* fields. Internally, PEP 526 *__annotations__* are used
to determine fields. In contrast to the Python implementation, this native approach
does not create a dataclass of the model.

.. c:var:: PyTypeObject CpStruct_Type

    The type object for the :code:`Struct` class.


There are a few differences between the Python implementation and this one. Although,
they try to be identical on the high-level programming interface, their low-level
implementation differs. For instance, because the C approach does not use the dataclass
module, methods such as :code:`__hash__`, :code:`__eq__`, and :code:`__repr__` are not
generated (at least for now).

.. c:type:: CpStructObject

    A core element of this library and is the base class for all structs. It is not
    recommended to extend this class, as its Python variant already covers possible
    subclass use-cases.

    All :code:`Struct` instances will store a reference to the core module state.
    There is no need to call :c:func:`get_global_core_state` more than once if you
    own a :code:`Struct` instance.


.. c:function:: CpStructObject *CpStruct_New(PyObject *model)

    Creates a new instance of a struct type and returns it. The *model* argument
    specifies the model of the struct and will be altered during struct initialization.
    Returns *NULL* if an error occurs.

    If passing custom options to the struct is necessary, the :c:var:`CpStruct_Type`
    should be called directly.


.. c:function:: int CpStruct_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpStructObject`.


.. c:function:: int CpStruct_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpStructObject`


.. c:function:: int CpStruct_AddFieldInfo(CpStructObject* o, CpStructFieldInfo* info)

    Adds a new field to the struct. Returns ``-1``. Returns ``0`` on success.


.. c:function:: int CpStruct_AddField(CpStructObject* o, CpField* field, int exclude)

    Adds a new field to the struct. If the field is already present, an exception
    will be set and the function returns ``-1``. The *exclude* flag will be passed
    on to the internal :c:type:`CpStructFieldInfo` instance. Returns ``0`` on success.


.. c:function:: PyObject* CpStruct_GetAnnotations(CpStructObject* self, int eval)

    Wrapper function around the :code:`get_annotations` function of the *inspect*
    module. The returned dictionary will be a copy of the original annotations.
    Returns *NULL* if an error occurs.


.. c:function:: int CpStruct_HasOption(CpStructObject *struct_, PyObject *option)

    Returns ``1`` if the struct has the given option, ``0`` otherwise.


.. c:function:: int CpStruct_ReplaceType(CpStructObject *struct_, PyObject *name, PyObject *type)

    Replaces the type of the given field in the underlying model. Returns ``0`` on
    success, ``-1`` on error.


.. c:function:: PyObject* CpStructModel_GetStruct(PyObject* m, _coremodulestate* s)

    Searches for :code:`__struct__` attribute in the given class and returns it,
    or *NULL* if not found. The state can be *NULL*.


.. c:function:: int CpStructModel_Check(PyObject* m, _coremodulestate* s)

    Returns ``1`` if the model stores a :c:type:`Struct` instance and therefore
    conforms to the *StructContainer* protocol, ``0`` otherwise. This function
    always suceeds if the given state is not *NULL*.


To manage field definitions, the :code:`Struct` class stores all discovered fields
in an internal dictionary using an extra type:

.. c:type:: CpStructFieldInfoObject

    Container class that stores a reference to the field from a struct. This type was
    introduced to store additional settings and configuration data for a field.


.. c:var:: PyTypeObject CpStructFieldInfo_Type

    The type object for the :c:type:`CpStructFieldInfoObject` class.


.. c:function:: CpStructFieldInfoObject* CpStructFieldInfo_New(CpFieldObject* field)

    Creates a new field info object and returns it. Returns *NULL* if an error occurs.


.. c:function:: int CpStructFieldInfo_Check(PyObject *op)

    Checks if the given object is an :c:type:`CpStructFieldInfoObject`


.. c:function:: int CpStructFieldInfo_CheckExact(PyObject *op)

    Checks if the given object is an instance of an :c:type:`CpStructFieldInfoObject`