# Caterpillar - 🐛

[![python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FMatrixEditor%2Fcaterpillar%2Fmaster%2Fpyproject.toml&logo=python)](https://www.python.org/downloads/)
[![Build and Deploy Docs](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-sphinx.yml/badge.svg)](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-sphinx.yml)
[![Run Tests](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-test.yml/badge.svg)](https://github.com/MatrixEditor/caterpillar/actions/workflows/python-test.yml)
![GitHub issues](https://img.shields.io/github/issues/MatrixEditor/caterpillar?logo=github)
![GitHub License](https://img.shields.io/github/license/MatrixEditor/caterpillar?logo=github)



> [!WARNING]
> This project is still in beta/testing phase. Expect bugs, naming changes and errors while using this
> library. C API Reference is WIP, C extensions are supported since v2.1.0.

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

## Installation

> [!NOTE]
> As of Caterpillar v2.1.2 it is possible to install the library without the need of
> compiling the C extension.

Simply use pip to install the package with all tools, all extra packages and the C extension:
```bash
pip install "caterpillar[all]@git+https://github.com/MatrixEditor/caterpillar.git"
```

> [!NOTE]
> You will need to install `make`, a C compiler and the Python3.12 development package.

If you just want to use the Python package without any native modules written in C,
you can specify the following environment variables:

* `CP_DISABLE_NATIVE` - Disables installation of the native C extension
* `CP_DISABLE_TOOLS` - Disables installation of extra tools

For instance, the following command will install the `caterpillar` package without
a native interface and without extra tools:
```bash
CP_DISABLE_NATIVE=TRUE \
CP_DISABLE_TOOLS=TRUE \
pip install git+https://github.com/MatrixEditor/caterpillar
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