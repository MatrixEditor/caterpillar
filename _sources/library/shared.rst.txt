.. _lib_shared:

Shared Concepts
===============

.. automodule:: caterpillar.shared

.. py:attribute:: ATTR_STRUCT
    :value: "__struct__"

    All models annotated with either ``@struct`` or ``@bitfield`` are struct
    containers. Thus, they store the additional class attribute :code:`__struct__`.

    Internally, any types utilizing this attribute can be employed within a
    struct, bitfield, or sequence definition. The type of the stored value
    must be conforming to the :class:`_StructLike` protocol.

    .. versionchanged:: 2.5.0
        This attribute is now used when callung :func:`getstruct` or :func:`hasstruct`.


.. py:attribute:: ATTR_BYTEORDER
    :value: "__byteorder__"

    .. versionadded:: 2.5.0
        Moved from *caterpillar.byteorder*.


.. py:attribute:: ATTR_TYPE
    :value: "__type__"

    .. versionadded:: 2.5.0


.. py:attribute:: ATTR_BITS
    :value: "__bits__"

    .. versionadded:: 2.5.0
        Moved from *caterpillar.model._bitfield*.


.. py:attribute:: ATTR_SIGNED
    :value: "__signed__"

    .. versionadded:: 2.5.0
        Moved from *caterpillar.model._bitfield*.


.. py:attribute:: ATTR_TEMPLATE
    :value: "__template__"

    .. versionadded:: 2.5.0
        Moved from *caterpillar.model._template*.


.. py:attribute:: ATTR_ACTION_PACK
    :value: "__action_pack__"

    .. versionadded:: 2.4.0


.. py:attribute:: ATTR_ACTION_UNPACK
    :value: "__action_unpack__"

    .. versionadded:: 2.4.0


.. py:attribute:: MODE_PACK
    :value: 0


.. py:attribute:: MODE_UNPACK
    :value: 1


.. autofunction:: getstruct

.. autofunction:: hasstruct

.. autofunction:: typeof

.. autoclass:: Action
