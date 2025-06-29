.. _ref_datamodel_protocol_bitfield_ext:

Bit-field Extensions
====================

The introduced :class:`~caterpillar.model.Bitfield` class is special in many different ways. One key
attribute is its fixed size. To determine the size of a struct, it leverages a special
member, which can be either a function or an attribute.

.. method:: object.__bits__(self)

    Called to measure the bit count of the current object. :meth:`~object.__bits__`
    serves as the sole requirement for the defined fields in the current implementation
    of the :class:`~caterpillar.model.Bitfield` class.

    .. note::
        This class member can also be expressed as an attribute. The library automatically
        adapts to the appropriate representation based on the context.

.. method:: object.__signed__(self)

    *Proposed for future use - currently unused*

Derived Protocols
-----------------

.. py:class:: _SupportsBits

    .. py:function:: __bits__(self) -> int


.. py:class:: _ContainsBits

    .. py:attribute:: __bits__
        :type: int

