# Caterpillar - 🐛

[![python](https://img.shields.io/badge/python-3.12+-blue.svg?logo=python&labelColor=grey)](https://www.python.org/downloads/)
![Codestyle](https://img.shields.io:/static/v1?label=Codestyle&message=black&color=black)
![License](https://img.shields.io:/static/v1?label=License&message=GNU+v3&color=blue)
![Status](https://img.shields.io:/static/v1?label=Status&message=🚧&color=teal)

> [!WARNING]
> This projectis stell in beta/testing phase. Expect bugs and errors while using this
> library.

Caterpillar is a Python 3.12+ library to pack and unpack structurized binary data. It
enhances the capabilities of [Python Struct](https://docs.python.org/3/library/struct.html)
by enabling direct class declaration. More information about the different configuration
options will be added in the future. A brief introduction can be found [here >](docs/INTRO.md).

## Installation

Simply use pip to install the package:
```console
pip install git+https://github.com/MatrixEditor/caterpillar.git
```

## Starting Point

Let's start off with a simple example: Consider we wan't do define our own file format
that stores blobs of data. We can simply re-create the structure of our file format
using python classes:

```python
from caterpillar.shortcuts import struct, be, this
from caterpillar.fields import * #(0)

@struct
class Image:
    signature: b'HDR'        # (1)
    length: be + uint16      # (2), be := BigEndian
    data: Bytes(this.length) # (3)
```

* **(0)**:
    A wildcard import should be used if there would be too many single imports

* **(1)**:
    As this library uses annotations to define the struct's we can use a constant
    value mark this field as a constant.

    > [!TIP]
    > Only ``bytes``, ``str`` values can be assigned to constant fields (**currently**)

* **(2)**:
    All integer types are defined without any endian configuration. You can simply add
    an endian type which may impact the way the field's value will be unpacked from the
    data stream.

* **(3)**:
    Using the struct ``Bytes`` together with a context lambda, we can define a dynamic
    sized struct. Note that the size can't be calculated of this class.

This class can be used to pack and unpack data directly:
```python
from caterpillar.shortcuts import pack, unpack

obj = Image(length=10, data=[i for i in range(10)])
data = pack(obj)
obj: Image = unpack(Image, data)
```

### Options

*TODO*

## License

Distributed under the GNU General Public License (V3). See [License](LICENSE) for more information.