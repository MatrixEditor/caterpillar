.. _context_lambda:

Context Lambdas
===============

Dynamic-sized structs are supported by this library through the use of so-called
*context lambdas*. The library introduces a special callable, :class:`_ContextLambda`,
which accepts a :class:`_ContextLike` instance and returns the desired result.

To implement a *context lambda*, a class must define the :meth:`__call__` method.

.. method:: object.__call__(self, context)

   The library does not distinguish between general callable objects and *context lambdas*;
   both are treated as instances of the same class.


Derived Protocols
-----------------

.. py:class:: _ContextLambda[_RT]

    .. py:function:: __call__(self, context: _ContextLike) -> _RT
