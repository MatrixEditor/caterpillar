.. _ref_datamodel_protocol_byteorder_ext:

Byteorder Extensions
====================

.. attribute:: object.__byteorder__

    The byteorder of a struct can be temporarily configured using the corresponding
    operator. It is important to note that this attribute is utilized internally and
    should not be used elsewhere.

    .. code-block:: python

        >>> struct = BigEndian | struct # Automatically sets __byteorder__


.. method:: object.__set_byteorder__(self, byteorder)

    In contrast to the attribute :attr:`~object.__byteorder__`, the :meth:`~object.__set_byteorder__`
    method is invoked to apply the current byteorder to a struct. The default behavior,
    as described in :class:`FieldMixin`, is to return a new :class:`~caterpillar.fields.Field` instance with
    the byteorder applied. Note the use of another operator here.

    >>> field = BigEndian + struct
