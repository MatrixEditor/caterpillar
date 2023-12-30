.. _model:

************
Struct Model
************

*TODO*


Base classes
------------

.. autoclass:: caterpillar.model.Sequence()
    :members:

.. autoclass:: caterpillar.model.Struct()
    :members:

.. autoclass:: caterpillar.model.BitFieldGroup
    :members:

.. autoclass:: caterpillar.model.BitField
    :members:

.. autoclass:: caterpillar.model.UnionHook
    :members:
    :special-members: __model_init__, __model_setattr__


Standard functions
------------------

.. autofunction:: caterpillar.model.struct

.. autofunction:: caterpillar.model.union

.. autofunction:: caterpillar.model.pack

.. autofunction:: caterpillar.model.pack_into

.. autofunction:: caterpillar.model.pack_file

.. autofunction:: caterpillar.model.unpack

.. autofunction:: caterpillar.model.unpack_file

.. autofunction:: caterpillar.model.bitfield

