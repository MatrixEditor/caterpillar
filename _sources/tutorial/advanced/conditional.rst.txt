.. _tutorial-advanced-conditionals:

Conditional Fields
==================

.. warning::
    This feature is not supported in Python 3.14+.

*Conditional fields* allow you to define fields in a struct that are included
or excluded based on certain conditions. This feature is especially useful when
working with versioned formats or optional fields that depend on runtime
conditions. You can easily achieve this using context-based lambdas, which are
built into the library.

How it works
------------

By using the `with` keyword in combination with conditional expressions, you can
bind certain fields to a specific condition. This allows you to include or exclude
fields dynamically, depending on the value of other fields or context.

Here's an example demonstrating how to use conditional fields for versioned structs:

.. code-block:: python
    :caption: Conditional fields (e.g. for versioned structs)

    @struct
    class Format:
        version: uint32
        # all following fields will be bound to the condition
        with this.version == 1:
            header: uint8

Key Concepts
------------

1. **`with` and Conditionals**:
   The :code:`with` keyword is used to define a block of fields that should only be
   included if the condition evaluates to :code:`True`. In the example above, the
   fields inside :code:`with this.version == 1` are included only when the :code:`version`
   field has a value of :code:`1`.

2. **`ElseIf` for Multiple Conditions**:
   For multiple conditions, use :code:`ElseIf` rather than :code:`Else`. The :code:`ElseIf`
   construct ensures that the next condition is checked only if the previous
   one was false. This is safer and more predictable than using a generic
   :code:`Else` clause, which could introduce unintended side effects by executing
   under unanticipated conditions.


Example: Versioned Struct
^^^^^^^^^^^^^^^^^^^^^^^^^

Conditional fields are particularly useful when dealing with versioned structs,
where the structure of the data may change based on the version number or other
factors. For example:

.. code-block:: python
    :caption: Conditional fields (e.g. for versioned structs)

    @struct
    class Format:
        version: uint32
        # all following fields will be bound to the condition
        with this.version == 1:
            length: uint8
            extra: uint8
            data: Bytes(this.length)
        # Use else-if over 'Else' alone
        with ElseIf(this.version == 2):
            name: CString(16)
            data: Prefixed(uint8)


Best Practices
---------------

- **Avoid Using `Else`**:
  It is **strongly recommended** to **avoid** using :code:`Else` for conditional field
  inclusion, as it can introduce unintended behavior if not properly managed.
  Instead, always use :code:`ElseIf` with an inverted condition to ensure more
  predictable and controlled struct parsing.


.. note::

    When using conditional fields, it's essential to remember that the struct's
    layout can change dynamically depending on the conditions. This flexibility
    makes it possible to define complex, version-dependent data structures.