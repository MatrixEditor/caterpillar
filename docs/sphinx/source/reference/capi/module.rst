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

    *TODO*

.. c:macro:: CpModule_SetupType(op)

    Sets up the type object for the given module object. Expands to:

    .. code-block:: c

        if (PyType_Ready(op) < 0)
            return NULL;
