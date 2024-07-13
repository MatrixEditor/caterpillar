.. _reference-capi_paddingatom:

*************
Padding Atoms
*************

*TODO: under construction*

.. c:var:: PyTypeObject CpPaddingAtom_Type

    The type object for the :c:type:`paddingatom` class.


.. c:type:: CpPaddingAtomObject


.. c:function:: int CpPaddingAtom_Pack(CpPaddingAtomObject* self, PyObject* value, CpLayerObject* layer)


.. c:function:: int CpPaddingAtom_PackMany(CpPaddingAtomObject* self, PyObject* value, CpLayerObject* layer)


.. c:function:: PyObject* CpPaddingAtom_Unpack(CpPaddingAtomObject* self, CpLayerObject* layer)


.. c:function:: PyObject* CpPaddingAtom_UnpackMany(CpPaddingAtomObject* self, CpLayerObject* layer)


Runtime Performance
-------------------

Measurements represent the accumulated runtime of one million calls to
:code:`unpack` or :code:`pack` using the corresponding implementation
in seconds.

.. list-table::
    :header-rows: 1
    :widths: 20 20 20 20 20

    * - Function
      - Caterpillar C [0]_
      - Caterpillar G [1]_
      - Caterpillar   [2]_
      - Construct     [3]_
    * - :code:`unpack`
      - 1.614697s
      - 2.100239s
      - 3.652622s
      - 2.235666s
    * - :code:`pack`
      - 0.968687s
      - 2.166108s
      - 4.845472s
      - 2.267463s


.. [0] C implementation
.. [1] global field instance
.. [2] local field instance
.. [3] Construct implementation