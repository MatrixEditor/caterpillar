.. _tutorial_advanced_operators_custom:

Custom Operators
================

In addition to the standard Python operators, *Caterpillar* allows you
to define custom operators tailored to specific use cases. These custom
operators can be used to create more expressive and domain-specific syntax
when defining structs and fields. For example, you can create an operator
that automatically generates an array of a fixed length, making your code
cleaner and more intuitive.

To define a custom operator, *Caterpillar* provides a mechanism using the
:code:`_infix_` function, which allows you to wrap a lambda or function as an
operator. This custom operator can then be applied to fields in a struct,
just like any other operator.

Here's an example that demonstrates how to define and use a custom operator:

.. code-block:: python

    from caterpillar.fields import _infix_

    M = _infix_(lambda s, count: s[count * 2])

    @struct
    class Format:
        values: uint16 /M/ 3

- **Pre-processing Stage**:
  Custom operators are applied during the **pre-processing** phase. This means
  that they don't directly affect the overall parsing or unpacking process. Instead,
  they modify the way a struct or field is defined before it is parsed. In the
  example above, the custom operator is used to modify the length of the array
  before the struct is processed.

- **Return Custom Structs**:
  Custom operators are useful for generating custom structs or configurations
  that simplify the definition of data layouts, especially when dealing with
  repetitive or dynamic patterns.

Limitations
-----------

While custom operators allow for a high degree of flexibility, they currently don't
modify the parsing process itself. Instead, they are primarily used to modify how
fields or structs are defined before they are processed by the rest of the framework.

