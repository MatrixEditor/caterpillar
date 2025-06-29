.. _ref_datamodel_protocol_contextlike:

Context-like Objects
====================

Caterpillar provides a dedicated protocol for working with context-like objects.
This protocol enables seamless access to context variables during data packing
and unpacking operations. It is consistently implemented by all context-related
classes within this package.

.. method:: object.__context_getattr__(self, path)

   Retrieves a value from the context based on the given path. It is
   implementation-dependent whether nested paths are supported; by default,
   multiple path elements are separated by a single dot.

   For example, given the path :code:`"foo.bar"`, the context implementation
   should first resolve the value associated with :code:`"foo"`, then retrieve
   the :code:`"bar"` attribute from that result.

.. method:: object.__context_setattr__(self, path, value)

   Sets the value of a context variable specified by the given path.
   Similar to :meth:`__context_getattr__`, multiple path elements are
   separated by a dot by default. Implementations should resolve the
   intermediate path components and update the target variable with the
   provided value.

.. attribute:: object._root

   References the root context object. This attribute provides access to the
   top-level context, which can be useful for resolving global context
   variables or for operations that require awareness of the entire
   context hierarchy. If no root context has been set, the current instance
   will be returned.


Derived Protocols
-----------------

.. py:class:: _ContextLike

    .. py:attribute:: _root: _ContextLike | None
    .. py:function:: __context_getattr__(self, path: str) -> Any: ...
                     __context_setattr__(self, path: str, value: Any) -> None: ...
                     __getitem__(self, key, /) -> Any: ...
                     __setitem__(self, key, value: Any, /) -> None: ...