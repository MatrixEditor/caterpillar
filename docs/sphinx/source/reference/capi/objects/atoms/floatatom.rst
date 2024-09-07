.. _reference-capi_floatatom:

***********
Float Atoms
***********

*TODO: under construction*

.. c:var:: PyTypeObject CpFloatAtom_Type

    The type object for the :c:type:`floatatom` class.


.. c:type:: CpFloatAtomObject


.. c:function:: int CpFloatAtom_Pack(CpFloatAtomObject* self, PyObject* value, CpLayerObject* layer)


.. c:function:: PyObject* CpFloatAtom_Unpack(CpFloatAtomObject* self, CpLayerObject* layer)



Runtime Performance
-------------------

Measurements represent the accumulated runtime of one million calls to
:code:`unpack` or :code:`pack` using the corresponding implementation
in seconds.

.. list-table::
    :header-rows: 1
    :widths: 20 20 20 20 20

    * - Function
      - Caterpillar   [0]_
      - Caterpillar G [1]_
      - Caterpillar C [2]_
      - Construct     [3]_
    * - :code:`unpack`
      - 3.311959
      - 2.211655
      - 0.738574
      - 1.241862
    * - :code:`pack`
      - 3.058688
      - 2.128918
      - 1.015825
      - 1.234711


.. [2] local field instance
.. [1] global field instance
.. [0] C implementation
.. [3] Construct :code:`Float32n`