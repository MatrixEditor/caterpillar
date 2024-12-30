.. _tutorial-templates:

Templates
=========

Yes, you read that correctly: *Caterpillar* supports class templates, similar
to the concept in C++. Templates allow you to create generic structures that
can be tailored with specific types when they are derived.

If you'd like more details about the design decisions and limitations regarding
templates, refer to the :ref:`ref-templates` section in the data model description.

Defining a Template
-------------------

You can define templates using a special syntax. First, you create **template type variables**,
and then you use them within your class definition. These templates can be instantiated
later with specific types or values.

.. code-block:: python
    :caption: A simple template definition

    A = TemplateTypeVar("A")

    @template(A, "B")       # <-- either strings or global variables
    class FormatTemplate:
        foo: A[uint8::]     # <-- prefixed generic array
        bar: B              # <-- this won't throw an exception, because
                            # 'B' is created temporarily.

- :code:`A` is a **template type variable** of an unknown generic type
- The class :code:`FormatTemplate` uses :code:`A` and:code: `B` as type parameters, but these types will be defined when the template is derived into a specific class.
- :code:`A[uint8::]` creates a **generic array** prefixed with the type :code:`uint8`.
- :code:`B` is used as a type in the field :code:`bar`. This type will be specified when the template is instantiated, and the library ensures no exceptions are thrown because :code:`B` is set dynamically during class definition.

Deriving a Template
-------------------

Once you have defined a template, you can create specific classes (known as
**derivations**) by providing the template with concrete types. This allows
you to reuse the logic from the template with different type combinations,
e.g. creating specialized structs.

.. code-block:: python
    :caption: Creating template derivations

    @struct
    class Format32(derive(FormatTemplate, A=uint32, B=uint32)): # <- Derived Struct
        baz: uint32

*Sub-templates* or partial templates allow you to create smaller, more focused templates based on an
existing template. When you derive a sub-template, only some of the template
parameters are provided initially, and others are deferred.

.. code-block:: python
    :caption: Creating a sub-template

    # template sub-classes are allowed as well
    FormatSubTemplate = derive(FormatTemplate, A=uint8, partial=True) # <- Derived Template

.. note::

    While you can pass **keyword arguments** to define template parameters, you can also use
    **positional arguments** if the original template decorator defines them in that way.

.. warning::

    Currently, there are some **limitations** with the template type variables, and **extended support**
    for this feature will be part of future enhancements in this project.
