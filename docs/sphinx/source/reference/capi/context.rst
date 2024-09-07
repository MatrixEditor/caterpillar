.. highlight:: python

.. _reference-capi_context:

****************
Context Protocol
****************

Caterpillar provides a special protocol for working with contexts. It is
designed to enable access to context variables while packing or unpacking
data. This procotol is implemented by *all* context-related classes in
this package.


.. py:method:: object.__context_getattr__(self, path) -> object
    :noindex:

    This function is used to retrieve a value from the context. It is implementation
    dependent whether nested paths are supported. By default, multiple path elements
    are sperated by a single dot.

    For example, consider the following path: :code:`"foo.bar"`. The context
    implementation should first resolve the value of :code:`"foo"` and then
    retrieve the value of :code:`"bar"` from the result.
