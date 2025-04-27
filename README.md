# Caterpillar - 🐛

[![python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FMatrixEditor%2Fcaterpillar%2Fmaster%2Fpyproject.toml&logo=python)](https://www.python.org/downloads/)
[![Build and Deploy Docs](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-sphinx.yml/badge.svg)](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-sphinx.yml)
[![Run Tests](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-test.yml/badge.svg)](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-test.yml)
![GitHub issues](https://img.shields.io/github/issues/MatrixEditor/caterpillar?logo=github)
![GitHub License](https://img.shields.io/github/license/MatrixEditor/caterpillar?logo=github)



> [!WARNING]
> This project is still in beta/testing phase. Expect bugs, naming changes and errors while using this
> library. C API Reference is WIP, C extensions are supported since v2.1.0.

> [!NOTE]
> Python 3.14 breaks `with` statements in class definitions since `__annotations__` are added at the end
> of a class definition. Therefore, `Digest` and conditional statements **ARE NOT SUPPORTED** in Python 3.14+.



Caterpillar is a Python 3.12+ library to pack and unpack structurized binary data. It
enhances the capabilities of [Python Struct](https://docs.python.org/3/library/struct.html)
by enabling direct class declaration. More information about the different configuration
options will be added in the future. Documentation is [here >](https://matrixeditor.github.io/caterpillar/).

*Caterpillar* is able to:

* Pack and unpack data just from processing Python class definitions (including support for bitfields, c++-like templates and c-like unions!),
* apply a wide range of data types (with endianess and architecture configuration),
* dynamically adapt structs based on their inheritance layout,
* reduce the used memory space using `__slots__`,
* allowing you to place conditional statements into class definitions,
* insert proper types into the class definition to support documentation and
* it helps you to create cleaner and more compact code.
* You can even extend Caterpillar and write your parsing logic in C or C++!!

## Give me some code!

```python
from caterpillar.py import *

@struct(order=LittleEndian)
class Format:
    magic: b"ITS MAGIC"       # Supports string and byte constants directly
    a: uint8                  # Primitive data types
    b: int32
    length: uint8             # String fields with computed lengths
    name: String(this.length) #  -> you can also use Prefixed(uint8)

    # wraps all following fields and creates a new attr
    # only for Python <= 3.13
    with Md5(name="hash", verify=True):
        # Sequences with prefixed, computed lengths
        names: CString[uint8::]


# Instantiation (keyword-only arguments, magic is auto-inferred):
obj = Format(a=1, b=2, length=3, name="foo", names=["a", "b"])
# Packing the object, reads as 'PACK obj FROM Format'
# objects of struct classes can be packed right away
blob = pack(obj, Format)
# results in: b'ITS MAGIC\x01\x02\x00\x00\x00\x03foo\x02a\x00b\x00\xf55...

# Unpacking the binary data, reads as 'UNPACK Format FROM blob'
obj2 = unpack(Format, blob)
assert obj2.hash == obj.hash
```

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

### C-extension installation

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