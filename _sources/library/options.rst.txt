.. _options:

*******
Options
*******

*TODO*

Options by type
---------------

Sequence options
^^^^^^^^^^^^^^^^


.. autodata:: caterpillar.options.S_DISCARD_UNNAMED

    Using this option, all *unnamed* fields will be discarded and won't be
    visible in the final result object. An *unnamed* field must follow the
    following naming convention:

    .. code-block:: bnf

        <unnamed> := '_' [0-9]*

    Therefore, it is possible to include more than one unnamed field, for
    example:

    .. code-block:: python
        :caption: Simple sequence with an unnamed field

        >>> schema = Seq({
        ...     "a": uint8,
        ...     "_": padding[10]
        ... }, options={opt.S_DISCARD_UNNAMED})
        >>> data = b"\xFF" + bytes(10)
        >>> unpack(schema, data)
        {'a': 255}
        >>> pack(_, schema)
        b'\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


.. autodata:: caterpillar.options.S_SLOTS

    Feature option that will create a new class with the :code:`__slots__` attribute
    to lower required space. Take the following two structs into consideration:

    .. code-block:: python

        @struct
        class DictClass:
            a: uint8
            b: uint8
            c: uint8
            d: uint8
            e: uint8
            f: uint8
            g: uint8

        @struct(options={opt.S_SLOTS})
        class SlotsClass:
            a: uint8
            b: uint8
            c: uint8
            d: uint8
            e: uint8
            f: uint8
            g: uint8

    Each struct stores seven fields in total, whereby :code:`Format2` uses :code:`__slots__`
    to store each member. We used `pympler <https://pympler.readthedocs.io/en/latest/>`_ to
    retireve the amount of occupied bytes per object:

    .. code-block:: python
        :caption: Size difference between a :code:`__slots__` class and a normal Python class

        >>> o1 = DictClass(*[0xFF]*7)
        >>> asizeof.asizeof(o1)
        712
        >>> o2 = SlotsClass(*[0xFF]*7)
        >>> asizeof.asizeof(o2)
        120

    In addition, the overall used memory will be reduced, because the defined type will
    also occupy less memory:

    .. code-block:: python

        >>> from sys import getsizeof
        >>> getsizeof(DictClass)
        1704
        >>> getsizeof(SlotsClass)
        936



.. autodata:: caterpillar.options.S_DISCARD_CONST

    This option will only discard constant fields.

.. autodata:: caterpillar.options.S_UNION

    Internal option to add union behaviour to the :code:`caterpillar.model.Struct` class.

.. autodata:: caterpillar.options.S_REPLACE_TYPES


.. autodata:: caterpillar.options.S_EVAL_ANNOTATIONS




Struct options
^^^^^^^^^^^^^^



Field options
^^^^^^^^^^^^^

.. autoattribute:: caterpillar.options.F_KEEP_POSITION

.. autoattribute:: caterpillar.options.F_DYNAMIC

.. autoattribute:: caterpillar.options.F_SEQUENTIAL

.. autoattribute:: caterpillar.options.F_OFFSET_OVERRIDE



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

