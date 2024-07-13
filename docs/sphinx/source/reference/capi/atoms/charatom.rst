.. _reference-capi_charatom:

**********
Char Atoms
**********

*TODO: under construction*

.. c:var:: PyTypeObject CpCharAtom_Type

    The type object for the :c:type:`charatom` class.


.. c:type:: CpCharAtomObject


.. c:function:: int CpCharAtom_Pack(CpCharAtomObject* self, PyObject* value, CpLayerObject* layer)


.. c:function:: PyObject* CpCharAtom_Unpack(CpCharAtomObject* self, CpLayerObject* layer)



Runtime Performance
-------------------

Measurements represent the accumulated runtime of one million calls to
:code:`unpack` or :code:`pack` using the corresponding implementation
in seconds.

.. list-table::
    :header-rows: 1
    :widths: 20 20 20 20

    * - Function
      - Caterpillar [1]_
      - Caterpillar G [2]_
      - Caterpillar C [3]_
    * - :code:`unpack`
      - 2.813911s
      - 1.948262s
      - 0.960612s
    * - :code:`pack`
      - 2.963965s
      - 2.137714s
      - 0.721222s


.. [1] local field instance
.. [2] global field instance
.. [3] C implementation