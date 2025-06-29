.. _ref_datamodel_protocol_actionlike:

Action-like Objects
===================

Action-like objects provide a flexible mechanism for performing custom operations
during data processing. Rather than directly reading, writing, or storing a value,
actions are defined to modify or interact with the data at various stages
of serialization or deserialization.

There are generally two kinds of actions that can be implemented:

.. method:: object.__action_pack__(self, context)

   Invoked when data is serialized. This method can be used for tasks
   such as calculating checksums, logging..

.. method:: object.__action_unpack__(self, context)

   Invoked when data is deserialized. This method is typically used
   for validation, verification, or any other operation that should run during
   unpacking process.

.. note::

   To implement an action-like object, only one of these methods needs to be defined;
   defining both is optional.


Derived Protocols
-----------------

.. py:class:: _ActionLike

    .. py:function:: __action_pack__(self, context: _ContextLike) -> None
                     __action_unpack__(self, context: _ContextLike) -> None

.. py:class:: _SupportsActionUnpack

    .. py:function:: __action_unpack__(self, context: _ContextLike) -> None


.. py:class:: _SupportsActionPack

    .. py:function:: __action_pack__(self, context: _ContextLike) -> None
