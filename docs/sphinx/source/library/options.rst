.. _options:

****************
Options / Flags
****************

*TODO*

Options by Type
---------------

Global options
^^^^^^^^^^^^^^

.. data:: caterpillar.options.O_ARRAY_FACTORY

    To control the returned array type, a factory class or method can be set
    in this option using its attached value. For instance, we can incorporate
    the :code:`numpy.ndarray` into our unpacked objects:

    .. code-block:: python

        from caterpillar.options import O_ARRAY_FACTORY
        from numpy import array

        # just set the option's value
        O_ARRAY_FACTORY.value = array


    With the new configuration applied, your unpacked objects will occupy less
    memory space. The following table shows the size of unpacked objects in bytes:

    .. list-table:: Object sizes between different configuration options
        :header-rows: 1
        :stub-columns: 1
        :widths: 10, 15, 15

        * - Configuration
          - :code:`formats/nibarchive`
          - :code:`formats/caf` [*]_
        * - Default configuration
          - 26520
          - 10608
        * - :code:`__slots__` classes
          - 14240
          - 3848
        * - Default configuration and :code:`numpy.ndarray`
          - 7520
          - 1232
        * - :code:`__slots__` classes and :code:`numpy.ndarray`
          - 6152
          - 384
        * - Original filesize
          - **1157**
          - **5433**

.. [*] A CAF audio comes with a special chunk type that stores only zeros. By ingoring
  the data in this chunk, we can achieve less bytes in memory than the file originally used.

Sequence options
^^^^^^^^^^^^^^^^

.. note::

  All sequence-related configuration options are applied to structs as well.


.. data:: caterpillar.options.S_DISCARD_UNNAMED

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


.. data:: caterpillar.options.S_DISCARD_CONST

    This option will only discard constant fields.



Struct options
^^^^^^^^^^^^^^

.. data:: caterpillar.options.S_SLOTS

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
    retrieve the amount of occupied bytes per object:

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

.. data:: caterpillar.options.S_REPLACE_TYPES

    This option was designed for documentation purposes only and should be
    used in that context only. It will alter the class' annotations and remove
    all :class:`caterpillar.fields.Field` instances.

    Consider the following struct:

    .. code-block:: python

      @struct
      class Format:
          a: uint8
          b: String(10)
          c: uuid

      # use the following line to enable type replacement globally
      opt.set_struct_flags(opt.S_REPLACE_TYPES)
      # otherwise, just add options={opt.S_REPLACE_TYPES} to the
      # @struct call.

    You will notice the difference in the following output on disabled
    type replacement (1) and enabled replacement (2):

    .. code-block:: python

      >>> Format.__annotations__ # (1)
      {'a': <FormatField(int) 'B'>, 'b': <String>, 'c': <uuid>}
      >>> Format.__annotations__ # (2)
      {'a': <class 'int'>, 'b': <class 'str'>, 'c': <class 'uuid.UUID'>}


.. data:: caterpillar.options.S_EVAL_ANNOTATIONS

  If you decide to use :code:`from __future__ import annotations`, you have to set this
  option for each struct in the scope of this import, because it will stringify all
  placed annotations. Therefore, they need to be executed before analyzed.

  .. caution::

    Use this option with caution! It may result in execution of untrusted code, be aware!

.. data:: caterpillar.options.S_UNION

    Internal option to add union behaviour to the :code:`caterpillar.model.Struct` class.



Field options
^^^^^^^^^^^^^

.. attribute:: caterpillar.options.F_KEEP_POSITION

.. attribute:: caterpillar.options.F_DYNAMIC

.. attribute:: caterpillar.options.F_SEQUENTIAL

.. attribute:: caterpillar.options.F_OFFSET_OVERRIDE



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

