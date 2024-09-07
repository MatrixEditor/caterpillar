.. _reference-capi_fieldatom:

******************
Field Atom Objects
******************

Python Field Atoms
------------------

.. c:var:: PyTypeObject CpFieldAtom_Type

    The type object for the :c:type:`CpFieldAtomObject` class.


.. c:type:: CpFieldAtomObject

    C implementation of the Python equivalent (:class:`~caterpillar.fields.FieldMixin`).

    A simple mixin to support operators used to create `Field` instances.


.. c:function:: int CpFieldAtom_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpFieldAtomObject`.


.. c:function:: int CpFieldAtom_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpFieldAtomObject`


.. c:macro:: CpFieldAtom_HEAD

    Inspired by :code:`PyObject_HEAD`, places the :c:type:`CpFieldAtomObject` at the
    beginning of the object's memory block. For instance the following code:

    .. code-block:: c

        struct FooAtom {
            CpFieldAtom_HEAD

            // other fields
        };

        extern PyTypeObject FooAtom_Type;

    The defined class is now a subclass of :c:type:`CpFieldAtomObject` and inherits
    all methods. Make sure you don't forget to initialize the type correctly in your
    module code:

    .. code-block:: c

        // ...
        FooAtom_Type.tp_base = &CpFieldAtom_Type;
        CpModule_SetupType(&FooAtom_Type);
        // ...


C Field Atoms
-------------

.. c:var:: PyTypeObject CpFieldCAtom_Type

    The type object for the :c:type:`CpFieldCAtomObject` class.


.. c:type:: CpFieldCAtomObject

    Field atom for C fields. Inherits from :c:type:`CpCAtomObject`.


.. c:function:: int CpFieldCAtom_CheckExact(PyObject *op)

    Checks if the given object is an :c:type:`CpFieldCAtomObject`.


.. c:function:: int CpFieldCAtom_Check(PyObject *op)

    Checks if the given object is instance of an :c:type:`CpFieldCAtomObject`


.. c:macro:: CpFieldCAtom_HEAD

    Inspired by :code:`PyObject_HEAD`, places the :c:type:`CpFieldCAtomObject` at the
    beginning of the object's memory block.


.. c:macro:: CpFieldCAtom_CATOM(self)

    Returns the :c:type:`CpCAtomObject` from the given object which must be a
    :c:type:`CpFieldCAtomObject`. This macro can be used to set the packing and
    unpacking implementations:

    .. code-block:: c

        static PyObject*
        fooatom_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
        {
            FooAtom *self = (FooAtom *)type->tp_alloc(type, 0);
            if (self != NULL) {
                // initialize the fields
                CpFieldCAtom_CATOM(self).ob_pack = (packfunc)fooatom_pack;
                CpFieldCAtom_CATOM(self).ob_unpack = (unpackfunc)fooatom_unpack;
                // ...
            }
            return (PyObject*)self;
        }

