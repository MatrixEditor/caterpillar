# Introduction

`caterpillar` is a powerful python framework designed to navigate through structured binary data. This framework operates as a declarative parser and builder using standard Python class definitions and annotations. Below are the key functions of this library:

* Pack and unpack classes to and from binary data
* Structs support union processing as well
* All structs are defined using standard python class syntax

> [!IMPORTANT]
> This library was developed in Python 3.12. While efforts have been made to support
> backward compatibility, usage with older versions is subject to approval. For optimal
> performance and stability, it is recommended to use `caterpillar` with Python 3.12 and
> above.

## Example

In `caterpillar`, a `Struct` represents a collection of both named and unnamed fields.

```python
@struct(order=BigEndian)
class Format:
    magic: b"HDR"
    width: uint8
    height: uint8
    pixels: uint8[this.width * this.height]
```

In this example:

* The `Format` struct is defined with an explicit byte order specification (`BigEndian`
  in this case).
* It includes named fields like magic, width, height, and field pixels. Note that
  we don't need to specify the magic parameter explicitly, its default value will
  be placed automatically.
* The pixels field is dynamically sized based on the values of width and height.

Now, let's explore how to use this Struct for packing and unpacking binary data:
```python
>>> obj = Format(width=2, height=2, pixels=[i for i in range(4)])
>>> pack(obj)
b'HDR\x02\x02\x00\x01\x02\x03'
>>> unpack(Format, b'HDR\x02\x02\x00\x01\x02\x03')
Format(magic=b'HDR', width=2, height=2, pixels=[0, 1, 2, 3])
```

The same applies to collections of `Format` objects:
```python
>>> items = [
...     Format(width=2, height=2, pixels=[i for i in range(4)]),
...     Format(width=0, height=0, pixels=[])
... ]
>>> pack(items, Format[2])
b'BMP\x02\x02\x00\x01\x02\x03BMP\x00\x00'
>>> unpack(Format[2], b'BMP\x02\x02\x00\x01\x02\x03BMP\x00\x00')
[Format(magic=b'BMP', width=2, height=2, pixels=[0, 1, 2, 3]), Format(magic=b'BMP', width=0, height=0, pixels=[])]
```

## Installation

To install this package locally, simply use pip:
```bash
pip install git+https://github.com/MatrixEditor/caterpillar.git
# or dev-mode
git clone https://github.com/MatrixEditor/caterpillar.git && pip install -e caterpillar
```

## Supported Options

Explore the list of natively supported options (or those proposed to be supported) within `caterpillar`. All code snippets were taken from the [nibarchive](/examples/nibarchive.py) example.

### Constant Values

Constant values can be integrated into your data structures in two ways:

```python
@struct(order=LittleEndian)
class NIBHeader:
    # Here we define a constant value, which will raise an exception
    # upon a different parsed value.
    magic: b"NIBArchive"
    # we could also use ConstBytes directly
    magic: ConstBytes(b"NIBArchive") or Const(b"NIBArchive", Bytes(10))
```

> [!NOTE]
> * Endianness modification applies only to top-level structs. When using the
>   Const struct, the modifier must be placed in front of Const.

### Structs

Integrating structs or classes marked with `@struct` into your binary data processing is straightforward. Here's an example:

```python
@struct(order=LittleEndian)
class NIBClassName:
    length: VarInt
    extras_count: VarInt
    # This struct will remove all extra null-bytes padding
    name: CString(this.length)
    # Arrays can be created just like this:
    extras: int32[this.extras_count]
```

Note: While custom struct classes support array creation, some modifiers listed below are not currently implemented (at least for now).

### Bitfields

*TODO*

### Enums

Utilize the standard `enum` module to incorporate enumeration classes using a special struct:

```python
class ValueType(enum.Enum): ...

@struct(order=LittleEndian)
class NIBValue:
    key: VarInt
    # NOTE the use of a default value; otherwise None would be set.
    type: Enum(ValueType, uint8, default=ValueType.UNKNOWN)
```


## Modifiers

Modifiers in `caterpillar` enhance code readability by assigning unique operators to specific
field configurations.

## Endianness `+`

Configure the byte order of fields using the `+` modifier. It can be applied class-wide or to individual fields:

```python
@struct(order=BigEndian)  # class-wide for all fields
class Format:
    foo: le + uint8  # or for each field
```

For more details on available endian encodings, refer to the [Python documentation on struct](https://docs.python.org/3/library/struct.html).

## Condition `//`

*TODO*

## Switch `>>`

Implement a switch field using the right shift operator. It accepts a dictionary with the corresponding value-struct mapping or a context function:

```python
@struct(order=LittleEndian)
class NIBValue:
    key: VarInt
    type: Enum(ValueType, uint8, ValueType.UNKNOWN)
    value: Field(this.type) >> {
        ValueType.INT8: int8,
        ValueType.INT16: int16,
        # ... other mappings ...
        DEFAULT_OPTION: Computed(ctx._value), # ctx-Context has to be used here
    }
```

## Offset `@`

Jump to specific addresses during processing with the `@` operator. Useful for nested structs and navigating within the binary data:

```python
@struct(order=LittleEndian)
class NIBArchive:
    header: NIBHeader
    objects: NIBObject[this.header.object_count] @ this.header.offset_objects
```

> [!CAUTION]
> If packing a very large object with offset-defined fields, consider using a temporary file to avoid excessive memory usage during processing. (set `use_tempfile` to True in `unpack`)

## Starting Point (old)

Let's start off with a simple example (The full code is available in the `examples/` directory):
Write a parser for the [NIBArchive](https://github.com/matsmattsson/nibsqueeze/blob/master/NibArchive.md)
file format only using python classes. *It has never been easier!*

1. Step: Create the header struct
    ```python
    from caterpillar.fields import *
    from caterpillar.shortcuts import struct, LittleEndian

    @struct(order=LittleEndian)
    class NIBHeader:
        # Here we define a constant value, which will raise an exception
        # upon a different parsed value.
        magic: b"NIBArchive"

        # Primitive types can be used just like this
        unknown_1: int32
        unknown_2: int32
        # ...
        value_count: int32
        offset_values: int32
        # --- other fields omitted ---
    ```

2. Step: We want to parse all values, so let's to define its corresponding struct:
    ```python
    @struct(order=LittleEndian)
    class NIBValue:
        key: VarInt
        # NOTE the use of a default value; otherwise None would be set.
        type: Enum(ValueType, uint8, ValueType.UNKNOWN)
        # The field below describes a simple switch-case structure.
        value: Field(this.type) >> {
            ValueType.INT8: int8,
            ValueType.INT16: int16,
            # --- other options ---
            ValueType.OBJECT_REF: int32,
            # The following line shows how to manually return the parsed value (in
            # this case it would be the result of this.type). NOTE that the value
            # is only stored temporarily in the current context (not this-context).
            #
            # If this option is not specified and none of the above matched the input,
            # an exception will be thrown.
            DEFAULT_OPTION: Computed(ctx._value),
        }
    ```

3. Step: Define the final file structure
    ```python
    @struct(order=LittleEndian)
    class NIBArchive:
        # Other structs can be referenced as simple as this
        header: NIBHeader

        # this field is marked with '@': The parser will jump temporarily
        # to the position specified after the operator. Use | F_KEEP_POSITION to
        # continue parsing from the resulting position
        # --- other fields snipped out ---
        values: NIBValue[this.header.value_count] @ this.header.offset_values
    ```

4. Step: pack and unpack files
    ```python
    from caterpillar.shortcuts import pack_file, unpack_file

    # parse files
    obj: NIBArchive = unpack_file(NIBArchive, "/path/to/file.nib")
    # pack files: Note the use of 'use_tempfile' here. It will first
    # write everything into a temporary file and ceopy it later on.
    pack_file(obj, "/path/to/destination.nib", use_tempfile=True)
    ```
