.. _reference-capi_boolatom:

**********
Bool Atoms
**********

*TODO: under construction*

.. c:var:: PyTypeObject CpBoolAtom_Type

    The type object for the :c:type:`boolatom` class.


.. c:type:: CpBoolAtomObject


.. c:function:: int CpBoolAtom_Pack(CpBoolAtomObject* self, PyObject* value, CpLayerObject* layer)


.. c:function:: PyObject* CpBoolAtom_Unpack(CpBoolAtomObject* self, CpLayerObject* layer)



Runtime Performance
-------------------

Measurements represent the accumulated runtime of one million calls to
:code:`unpack` or :code:`pack` using the corresponding implementation
in seconds.

.. list-table::
    :header-rows: 1
    :widths: 20 20 20 20

    * - Function
      - Caterpillar C [0]_
      - Caterpillar G [1]_
      - Caterpillar   [2]_
    * - :code:`unpack`
      - 0.716998s
      - 2.109347s
      - 2.999292s
    * - :code:`pack`
      - 0.883599s
      - 2.036922s
      - 2.815762s


.. [2] local field instance
.. [1] global field instance
.. [0] C implementation