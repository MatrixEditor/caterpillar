.. _reference-capi_module:

**********
Module API
**********


.. c:var:: PyModuleDef CpModule;

    Global module object for the Caterpillar C module.


.. c:function:: inline _modulestate *get_module_state(PyObject *module)

    Returns the :c:type:`_modulestate` for the given module.


.. c:function:: inline _modulestate *get_global_module_state(void)

    Returns the :c:type:`_modulestate` using the global caterpillar module object.


.. c:struct:: _modulestate

    The internal state for this module. It will store all necessary information
    about the core module.

    Global options:

    .. c:member:: PyObject* cp_option__dynamic;
                  PyObject* cp_option__sequential;
                  PyObject* cp_option__keep_position;
                  PyObject* cp_option__union;
                  PyObject* cp_option__eval;
                  PyObject* cp_option__discard_unnamed;
                  PyObject* cp_option__discard_const;
                  PyObject* cp_option__replace_types;
                  PyObject* cp_option__slots;

    Global default options:

    .. c:member:: PyObject* cp_option__global_field_options;
                  PyObject* cp_option__global_struct_options;

    Global arch and endian:

    .. c:member:: PyObject* cp_arch__host;
                  PyObject* cp_endian__native;
                  PyObject* cp_endian__big;
                  PyObject* cp_endian__little;

    Typing constants:

    .. c:member:: PyObject* Any_Type;
                  PyObject* List_Type;
                  PyObject* Union_Type;
                  PyObject* BytesIO_Type;

    String constants:

    .. c:member:: PyObject* str_path_delim = ".";
                  PyObject* str_tell = "tell";
                  PyObject* str_seek = "seek";
                  PyObject* str_write = "write";
                  PyObject* str_read = "read";
                  PyObject* str_close = "close";
                  PyObject* str_strict = "strict";
                  PyObject* str___pack__ = "__pack__";
                  PyObject* str___pack_many__ = "__pack_many__";
                  PyObject* str___unpack__ = "__unpack__";
                  PyObject* str___unpack_many__ = "__unpack_many__";
                  PyObject* str___size__ = "__size__";
                  PyObject* str___type__ = "__type__";
                  PyObject* str___annotations__ = "__annotations__";
                  PyObject* str___mro__ = "__mro__";
                  PyObject* str___struct__ = "__struct__";
                  PyObject* str___slots__ = "__slots__";
                  PyObject* str___match_args__ = "__match_args__";
                  PyObject* str___weakref__ = "__weakref__";
                  PyObject* str___dict__ = "__dict__";
                  PyObject* str___qualname__ = "__qualname__";
                  PyObject* str_start = "start";
                  PyObject* str_ctx__root = "<root>";
                  PyObject* str_ctx__getattr = "__context_getattr__";
                  PyObject* str_bytesio_getvalue = "getvalue";
                  PyObject* str_builder_process = "process";
                  PyObject* str_pattern_match = "match";

.. c:macro:: CpModule_SetupType(op)

    Sets up the type object for the given module object. Expands to:

    .. code-block:: c

        if (PyType_Ready(op) < 0)
            return NULL;
