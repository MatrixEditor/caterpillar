# Introduction

`caterpillar` is a powerful python frameworkdesigned to effortlessly navigate through structured binary data. This framework operates as a declarative parser and builder, streamlining the handling of binary data through the utilization of standard Python class definitions and annotations. Below are the key functions of this library:

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
This powerful feature facilitates the seamless organization and manipulation of
structured binary data.

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

Explore the list of natively supported options (or those proposed to be supported) within `caterpillar`:

### Constant Values

Constant values can be seamlessly integrated into your data structures in two ways:

```python
@struct
class Format:
    signature: b"HDR"
    magic: "FOO"
    # or by using a custom type
    const: Const(0x1234, uint32)
```

> [!NOTE]
> * Endianness modification applies only to top-level structs. When using the
>   Const struct, the modifier must be placed in front of Const.

### Structs

*TODO*

## Modifiers

### Endian

*TODO*

### Condition `//`

*TODO*

### Switch `>>`

*TODO* (not stable, under construction)

### Offset `@`

*TODO*

### Flags `|` and `^`

*TODO*

### Sequence `[]`

*TODO*