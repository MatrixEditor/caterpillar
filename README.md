# Caterpillar - 🐛

[![python](https://img.shields.io/badge/python-3.12+-blue.svg?logo=python&labelColor=grey)](https://www.python.org/downloads/)
![Codestyle](https://img.shields.io:/static/v1?label=Codestyle&message=black&color=black)
![License](https://img.shields.io:/static/v1?label=License&message=GNU+v3&color=blue)
![Status](https://img.shields.io:/static/v1?label=Status&message=🚧&color=teal)

> [!WARNING]
> This project is stell in beta/testing phase. Expect bugs, naming changes and errors while using this
> library.

Caterpillar is a Python 3.12+ library to pack and unpack structurized binary data. It
enhances the capabilities of [Python Struct](https://docs.python.org/3/library/struct.html)
by enabling direct class declaration. More information about the different configuration
options will be added in the future. A brief introduction can be found [here (outdated)](docs/INTRO.md) - documentation is [here >](https://matrixeditor.github.io/caterpillar/).

*Caterpillar* is able to:

* Pack and unpack data just from processing Python class definitions (including support for bitfields with a c++ like syntax!),
* apply a wide range of data types (with endianess and architecture configuration),
* dynamically adapt structs based on their inheritance layout,
* inserts proper types into the class definition to support documentation and
* it helps you to create cleaner and more compact code.

## Installation

Simply use pip to install the package:
```console
pip install git+https://github.com/MatrixEditor/caterpillar.git
```

## Stating Point

Please visit the [Documentation](https://matrixeditor.github.io/caterpillar/), it contains a complete tutorial on how to use this library.

## Other Approaches

A list of similar approaches to parsing structured binary data with Python can be taken from below:

* [construct](https://github.com/construct/construct)
* [kaitai_struct](https://github.com/kaitai-io/kaitai_struct)
* [hachoir](https://hachoir.readthedocs.io/en/latest/)
* [mrcrowbar](https://github.com/moralrecordings/mrcrowbar)

## License

Distributed under the GNU General Public License (V3). See [License](LICENSE) for more information.