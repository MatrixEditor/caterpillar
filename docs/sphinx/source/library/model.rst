.. _model:

************
Struct Model
************

*TODO*

.. toctree::
    :maxdepth: 2

    model/bitfield.rst

Base classes
------------

.. autoclass:: caterpillar.py.Action

    .. versionadded:: 2.4.0

.. autoclass:: caterpillar.model.Sequence()
    :members:

.. autoclass:: caterpillar.model.Struct()
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


Templates
---------

.. autoclass:: caterpillar.model.TemplateTypeVar
    :members:

.. autofunction:: caterpillar.model.istemplate


.. autofunction:: caterpillar.model.template


.. autofunction:: caterpillar.model.derive


