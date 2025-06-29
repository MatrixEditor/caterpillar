.. _library_model_struct:

======
Struct
======

.. py:currentmodule:: caterpillar.model


The *Struct* class
------------------

.. autoclass:: caterpillar.model.Struct
    :members:


Unions
------

.. autofunction:: caterpillar.model.union

.. autoclass:: caterpillar.model.UnionHook
    :members:
    :special-members: __model_init__, __model_setattr__


Standard Interface
------------------

.. autofunction:: caterpillar.model.struct

.. autofunction:: caterpillar.model.pack

.. autofunction:: caterpillar.model.pack_into

.. autofunction:: caterpillar.model.pack_file

.. autofunction:: caterpillar.model.unpack

.. autofunction:: caterpillar.model.unpack_file

.. autofunction:: caterpillar.model.sizeof

    .. versionchanged:: 2.5.0

        Now checks if the provided object implements the :class:`_SupportsSize` protocol