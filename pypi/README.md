# Caterpillar - 🐛

[![python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=yellow)](https://www.python.org/downloads/)
![![Latest Version](https://pypi.org/project/caterpillar-py/)](https://img.shields.io/github/v/release/MatrixEditor/caterpillar.svg?logo=github&label=Latest+Version)
[![Build and Deploy Docs](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-sphinx.yml/badge.svg)](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-sphinx.yml)
[![Run Tests](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-test.yml/badge.svg)](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-test.yml)
![GitHub issues](https://img.shields.io/github/issues/MatrixEditor/caterpillar?logo=github)
![GitHub License](https://img.shields.io/github/license/MatrixEditor/caterpillar?logo=github)


Caterpillar is a Python 3.12+ library to pack and unpack structurized binary
data (with support for 3.10+). It enhances the capabilities of [Python Struct](https://docs.python.org/3/library/struct.html)
by enabling direct class declaration. More information about the different configuration
options will be added in the future. Documentation is [here >](https://matrixeditor.github.io/caterpillar/).

*Caterpillar* is able to:

* Pack and unpack data just from processing Python class definitions (including support for powerful bitfields, c++-like templates and c-like unions!),
* apply a wide range of data types (with endianess and architecture configuration),
* dynamically adapt structs based on their inheritance layout,
* reduce the used memory space using `__slots__`,
* allowing you to place conditional statements into class definitions,
* insert proper types into the class definition to support documentation and
* it helps you to create cleaner and more compact code.
* There is also a feature that lets you dynamically change the endian within a struct!
* You can even extend Caterpillar and write your parsing logic in C or C++
* All struct definitions can be typing compliant!!! (tested with pyright)

## Give me some code!

*The following code is typing compliant, meaning your static type checker won't*
*scream at you when developing with this code*.

<details>
<summary><i>If you want to check out the default syntax, open this block.</i></summary>

```python
from caterpillar.py import *
from caterpillar.types import *

@bitfield(order=LittleEndian)
class Header:
    version : 4                   # 4bit integer
    valid   : 1                   # 1bit flag (boolean)
    ident   : (8, CharFactory)    # 8bit char
    # automatic alignment to 16bits

THE_KEY = b"ITS MAGIC"

@struct(order=LittleEndian, kw_only=True)
class Format:
    magic  : THE_KEY                      # Supports string and byte constants directly
    header : Header
    a      : uint8                        # Primitive data types
    b      : Dynamic + int32              # dynamic endian based on global config
    length : uint8                        # String fields with computed lengths
    name   : String(this.length)          #  -> you can also use Prefixed(uint8)

    # custom actions, e.g. for hashes
    _hash_begin : DigestField.begin("hash", Md5_Algo)
    # Sequences with prefixed, computed lengths    -+ part of the MD5 hash
    names       : CString[uint8::]               #  |
    #                                              -+
    # automatic hash creation and verification + default value
    hash        : Md5_Field("hash", verify=True)

# Creation, packing and unpacking remains the same
```

</details>

```python
from caterpillar.py import *
from caterpillar.types import *

@bitfield(order=LittleEndian)
class Header:
    version : int4_t                   # 4bit integer
    valid   : int1_t                   # 1bit flag (boolean)
    ident   : f[str, (8, CharFactory)] # 8bit char
    # automatic alignment to 16bits

THE_KEY = b"ITS MAGIC"

@struct(order=LittleEndian, kw_only=True)
class Format:
    magic  : f[bytes, THE_KEY] = THE_KEY  # Supports string and byte constants directly
    header : Header
    a      : uint8_t                      # Primitive data types
    b      : f[int, Dynamic + int32]      # dynamic endian based on global config
    length : uint8_t                      # String fields with computed lengths
    name   : f[str, String(this.length)]  #  -> you can also use Prefixed(uint8)

    # custom actions, e.g. for hashes
    _hash_begin : f[None, DigestField.begin("hash", Md5_Algo)] = None
    # Sequences with prefixed, computed lengths    -+ part of the MD5 hash
    names       : f[list[str], CString[uint8::]] #  |
    #                                              -+
    # automatic hash creation and verification + default value
    hash        : f[bytes, Md5_Field("hash", verify=True)] = b""

# Creation (keyword-only arguments, magic is auto-inferred):
obj = Format(
    header=Header(version=2, valid=True, ident="F"),
    a=1,
    b=2,
    length=3,
    name="foo",
    names=["a", "b"]
)

# Packing the object; reads as 'PACK obj FROM Format'
# objects of struct classes can be packed right away
data_le = pack(obj, Format)
# results in: b'ITS MAGIC0*\x01\x02\x00\x00\x00\x03foo\x02a\x00b\x00)\x9a...'

# Unpacking the binary data, reads as 'UNPACK Format FROM blob'
obj2 = unpack(Format, data_le)
assert obj2.names == obj.names

# to pack with a different endian for fields 'a' and 'b', use 'order'
data_be = pack(obj, Format, order=BigEndian)
assert data_le != data_be
```

> [!NOTE]
> Python 3.14 breaks `with` statements in class definitions since `__annotations__` are added at the end
> of a class definition. Therefore, `Digest` and conditional statements **ARE NOT SUPPORTED** using the `with` syntax in Python 3.14+.
> As of version `2.4.5` the `Digest` class has a counterpart (`DigestField`), which can be used to manually specify a digest without
> the need of a `ẁith` statement.

This library offers extensive functionality beyond basic struct handling. For further details
on its powerful features, explore the official [documentation](https://matrixeditor.github.io/caterpillar/),
[examples](./examples/), and [test cases](./test/).

## Installation

> [!NOTE]
> As of Caterpillar v2.1.2 it is possible to install the library without the need of
> compiling the C extension.

### PIP installation (Python-only)

```bash
pip install caterpillar-py
```

### Python-only installation

```bash
pip install "caterpillar[all]@git+https://github.com/MatrixEditor/caterpillar"
```

### Installation + C-extension

```bash
pip install "caterpillar[all]@git+https://github.com/MatrixEditor/caterpillar/#subdirectory=src/ccaterpillar"
```


## Starting Point

Please visit the [Documentation](https://matrixeditor.github.io/caterpillar/), it contains a complete tutorial on how to use this library.

## Other Approaches

A list of similar approaches to parsing structured binary data with Python can be taken from below:

* [construct](https://github.com/construct/construct)
* [kaitai_struct](https://github.com/kaitai-io/kaitai_struct)
* [hachoir](https://hachoir.readthedocs.io/en/latest/)
* [mrcrowbar](https://github.com/moralrecordings/mrcrowbar)

The documentation also provides a [Comparison](https://matrixeditor.github.io/caterpillar/reference/introduction.html#comparison)
to these approaches.

## License

Distributed under the GNU General Public License (V3). See [License](LICENSE) for more information.