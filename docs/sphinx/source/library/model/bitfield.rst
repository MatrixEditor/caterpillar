.. _library_model_bitfield:

========
Bitfield
========

.. versionchanged:: 2.5.0
    New revised concept since v2.5.0.

.. py:currentmodule:: caterpillar.model

Main Interface
--------------

.. autoclass:: Bitfield
    :members:

    .. versionchanged:: 2.5.0
        Updated concept. See the _reference_ for more information.

.. autoclass:: BitfieldGroup
    :members:

    .. versionchanged:: 2.5.0
        Renamed from ``BitFieldGroup`` to ``BitfieldGroup``

.. autoclass:: BitfieldEntry
    :members:

    .. versionadded:: 2.5.0


.. autofunction:: getbits

.. autofunction:: issigned

.. autofunction:: bitfield

    .. versionchanged:: 2.5.0
        Added the ``alignment`` parameter.

Default Factory Classes
-----------------------

.. autoclass:: BitfieldValueFactory
    :members:

    .. versionadded:: 2.5.0

.. autoclass:: CharFactory
    :members:

    .. versionadded:: 2.5.0

.. autoclass:: EnumFactory
    :members:

    .. versionadded:: 2.5.0


Default Options
---------------

.. py:attr:: EndGroup

    .. versionadded:: 2.5.0

    Alias for the :attr:`B_GROUP_NEW` flag, used to indicate that a new bitfield group should be started.


.. py:attr:: NewGroup

    Alias for the :attr:`B_GROUP_END` flag, used to indicate that the current bitfield group should be finalized.


.. autoclass:: SetAlignment
    :members:
