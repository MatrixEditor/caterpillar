.. _options:

*******
Options
*******

*TODO*

Interface
---------

.. autoclass:: caterpillar.options.Flag
    :members:

.. autofunction:: caterpillar.options.configure

.. autofunction:: caterpillar.options.set_struct_flags

.. autofunction:: caterpillar.options.set_field_flags

.. autofunction:: caterpillar.options.set_union_flags

.. autofunction:: caterpillar.options.get_flags

.. autofunction:: caterpillar.options.has_flag

.. autofunction:: caterpillar.options.get_flag


Options by type
---------------

Sequence options
^^^^^^^^^^^^^^^^


.. autoattribute:: caterpillar.options.S_DISCARD_UNNAMED

.. autoattribute:: caterpillar.options.S_DISCARD_CONST

.. autoattribute:: caterpillar.options.S_UNION

.. autoattribute:: caterpillar.options.S_REPLACE_TYPES

.. autoattribute:: caterpillar.options.S_EVAL_ANNOTATIONS


Field options
^^^^^^^^^^^^^

.. autoattribute:: caterpillar.options.F_KEEP_POSITION

.. autoattribute:: caterpillar.options.F_DYNAMIC

.. autoattribute:: caterpillar.options.F_SEQUENTIAL

.. autoattribute:: caterpillar.options.F_OFFSET_OVERRIDE


Other options
^^^^^^^^^^^^^

.. autoattribute:: caterpillar.fields.VARINT_LSB

