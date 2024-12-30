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



Python vs. Caterpillar C Syntax
-------------------------------

The type names in *caterpillar* differ slightly depending on the platform you're working with. Below
is a comparison between the Python and Caterpillar C variants:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - **Python**
      - **Caterpillar C**
    * - `int8`, `uint8`, `int16`, `uint16`, etc.
      - `i8`, `u8`, `i16`, `u16`, etc.
    * - `float16`, `float32`, `float64`
      - `f16`, `f32`, `f64`
    * - `boolean`, `char`, `void_ptr`
      - `boolean`, `char`

For more details, see :ref:`api-ctypes_int`


Custom-sized Integers
---------------------

In *Caterpillar*, you can define integers with custom sizes in bits, allowing you to work with non-standard
bit lengths. When defining these integers, you specify the bit count, and *Caterpillar* internally ensures
that only the necessary number of bytes are used.

For example, you can define a 24-bit signed integer or a 40-bit unsigned integer:

.. tab-set::

    .. tab-item:: Python

        >>> uint24 = Int(24)      # three-byte signed integer
        >>> uint40 = UInt(40)     # five-byte unsigned integer


    .. tab-item:: Caterpillar C

        >>> i48 = Int(48)               # six-byte signed integer
        >>> u40 = Int(40, signed=False) # five-byte unsigned integer

Variable-sized Integer
----------------------

The :class:`.py.VarInt`/:class:`.c.VarInt` type in both *Python* and *Caterpillar C* allows you to handle
integers with variable lengths, which is useful when the size of the integer can change depending on the
data being packed or unpacked. This type automatically adjusts the number of bytes required based on the value.

.. tab-set::

    .. tab-item:: Python

        >>> field = F(vint) # or F(VarInt())

    .. tab-item:: Caterpillar C

        >>> # use 'varint' directly or use VarInt()
        >>> be_varint = BIG_ENDIAN + varint
        >>> le_varint = VarInt(little_endian=True)

