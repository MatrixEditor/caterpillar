.. _tutorial-basics-stdtypes_numeric:

**************
Numeric Types
**************

When working with binary data, numbers are integral to structuring and
interpreting the data. Beyond the default integer types (such as :code:`uint8`,
:code:`uint16`, etc.), *caterpillar* introduces specialized integer formats
to accommodate various binary data representations.

The library supports several types of numbers, categorized into integers,
floating point numbers, and special primitives. Below are the available types:

Integer Types
-------------

**Unsigned** and **signed** integers are the most commonly used types for
storing numeric values. The following integer types are available:

- **Signed** Integers:
    - `int8`, `int16`, `int24`, `int32`, `int64`, see :ref:`fields-common`

- **Unsigned** Integers:
    - `uint8`, `uint16`, `uint24`, `uint32`, `uint64`, see :ref:`fields-common`

- **Platform-Specific** Sizes:
    - `ssize_t`, `size_t` (signed and unsigned sizes), see :ref:`fields-common`

Floating Point Types
--------------------

For floating-point numbers, *caterpillar* offers the following types:

- `float16`, `float32`, `float64`, see :ref:`fields-common`


Special Primitives
------------------

In addition to numbers, there are some special primitive types that are often
used in binary data manipulation:

- `boolean`: A boolean value (True/False)
- `char`: A single character
- `void_ptr`: A void pointer, typically used in scenarios involving memory addresses or raw data pointers



Custom-sized Integers
---------------------

In *Caterpillar*, you can define integers with custom sizes in bits, allowing you to work with non-standard
bit lengths. When defining these integers, you specify the bit count, and *Caterpillar* internally ensures
that only the necessary number of bytes are used.

For example, you can define a 24-bit signed integer or a 40-bit unsigned integer:

>>> uint24 = Int(24)      # three-byte signed integer
>>> uint40 = UInt(40)     # five-byte unsigned integer


Variable-sized Integer
----------------------

The :class:`.py.VarInt`/:class:`.c.VarInt` type in both *Python* and *Caterpillar C* allows you to handle
integers with variable lengths, which is useful when the size of the integer can change depending on the
data being packed or unpacked. This type automatically adjusts the number of bytes required based on the value.

>>> field = F(vint) # or F(VarInt())

.. versionchanged:: 2.6.0
    ``vint`` is now usable without a ``Field`` wrapper.

