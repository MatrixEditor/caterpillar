.. _context:

*******
Context
*******

Context classes
---------------

.. autoclass:: caterpillar.context.Context
    :members: __context_getattr__, __context_setattr__, _root

    Represents the primary container for context-aware operations during packing
    and unpacking. It manages attribute access, supports hierarchical
    relationships, and tracks contextual state. Conforms to the
    :class:`_ContextLike` protocol.


.. autoclass:: caterpillar.context.ContextPath
    :members: __call__, __getattribute__, __repr__, parent, parentctx

.. autoclass:: caterpillar.context.ContextLength
    :members:

    Encapsulates length information derived from the context, often used in
    size-dependent field evaluation.


.. autoclass:: caterpillar.context.ConditionContext


.. autoclass:: caterpillar.context.SetContextVar
    :members: __action_pack__, __action_unpack__


Extra options
-------------

.. autoattribute:: caterpillar.context.O_CONTEXT_FACTORY

    Defines the default factory used to instantiate context objects during the
    packing and unpacking process. To use the C-extension :code:`Context`
    implementation for a 10% speed caveat, use:

    .. code-block:: python

        from caterpillar.context import O_CONTEXT_FACTORY
        from caterpillar.c import c_Context

        # that's all you have to do
        O_CONTEXT_FACTORY.value = c_Context

    .. versionadded:: 2.6.0


Special paths
-------------

.. autoattribute:: caterpillar.context.this

.. autoattribute:: caterpillar.context.ctx

.. autoattribute:: caterpillar.context.parent

.. autoattribute:: caterpillar.context.parentctx

    .. versionadded:: 2.8.0

.. autoattribute:: caterpillar.context.root

    Provides access to the root-level context object.

    .. versionadded:: 2.6.0


Special Attributes
------------------

.. autoattribute:: caterpillar.context.CTX_PARENT

    Identifies the parent object within the context tree.

.. autoattribute:: caterpillar.context.CTX_OBJECT

    Refers to the current object associated with the context.

.. autoattribute:: caterpillar.context.CTX_OFFSETS

    Stores offset information used during stream parsing or generation.

.. autoattribute:: caterpillar.context.CTX_STREAM

    References the data stream associated with the packing or unpacking operation.

.. autoattribute:: caterpillar.context.CTX_FIELD

    Indicates the current field being processed within the structure.

.. autoattribute:: caterpillar.context.CTX_VALUE

    Stores the value associated with the current context node.

.. autoattribute:: caterpillar.context.CTX_POS

    Represents the current position within the stream or structure.

.. autoattribute:: caterpillar.context.CTX_INDEX

    Maintains the index for sequence or array-based context elements.

.. autoattribute:: caterpillar.context.CTX_PATH

    Provides the full path to the current context object.

.. autoattribute:: caterpillar.context.CTX_SEQ

    Holds a reference to the sequence object, if applicable.

.. autoattribute:: caterpillar.context.CTX_ROOT

    Points to the root of the entire context hierarchy.

.. autoattribute:: caterpillar.context.CTX_ORDER

    Stores the currently used endianess (only in root context).

    .. versionadded:: 2.7.0

.. autoattribute:: caterpillar.context.CTX_ARCH

    Stores the currently used architecture (only in root context).

    .. versionadded:: 2.7.0


Expressions
-----------

.. autoclass:: caterpillar.context.ExprMixin
    :members:

.. autoclass:: caterpillar.context.BinaryExpression
    :members:

.. autoclass:: caterpillar.context.UnaryExpression
    :members: