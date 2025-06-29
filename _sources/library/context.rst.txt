.. _context:

*******
Context
*******

*TODO*

Context classes
---------------

.. autoclass:: caterpillar.context.Context
    :members: __context_getattr__, __context_setattr__, _root

.. autoclass:: caterpillar.context.ContextPath
    :members:

.. autoclass:: caterpillar.context.ContextLength
    :members:

.. autoclass:: caterpillar.context.ConditionContext


Special paths
-------------

.. autoattribute:: caterpillar.context.this

.. autoattribute:: caterpillar.context.ctx

.. autoattribute:: caterpillar.context.parent

Special Attributes
------------------

.. autoattribute:: caterpillar.context.CTX_PARENT

.. autoattribute:: caterpillar.context.CTX_OBJECT

.. autoattribute:: caterpillar.context.CTX_OFFSETS

.. autoattribute:: caterpillar.context.CTX_STREAM

.. autoattribute:: caterpillar.context.CTX_FIELD

.. autoattribute:: caterpillar.context.CTX_VALUE

.. autoattribute:: caterpillar.context.CTX_POS

.. autoattribute:: caterpillar.context.CTX_INDEX

.. autoattribute:: caterpillar.context.CTX_PATH

.. autoattribute:: caterpillar.context.CTX_SEQ

.. autoattribute:: caterpillar.context.CTX_ROOT


Expressions
-----------

.. autoclass:: caterpillar.context.ExprMixin
    :members:

.. autoclass:: caterpillar.context.BinaryExpression
    :members:

.. autoclass:: caterpillar.context.UnaryExpression
    :members: