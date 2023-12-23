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
options will be added in the future. A brief introduction can be found [here >](docs/INTRO.md).

*Caterpillar* is able to:

* Pack and unpack data just from processing Python class definitions (including support for bitfields with a c++ like syntax!),
* apply a wide range of data types (with endianess and architecture configuration),
* dynamically adapt structs based on their inheritance layout,
* inserts proper types into the class definition to support documentation and
* it helps you to create cleaner and more concise code.

## Installation

Simply use pip to install the package:
```console
pip install git+https://github.com/MatrixEditor/caterpillar.git
```

## Starting Point

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


## Other Approaches

A list of similar approaches to parsing structured binary data with Python can be taken from below:

* [construct](https://github.com/construct/construct)
* [kaitai_struct](https://github.com/kaitai-io/kaitai_struct)
* [hachoir](https://hachoir.readthedocs.io/en/latest/)
* [mrcrowbar](https://github.com/moralrecordings/mrcrowbar)

## License

Distributed under the GNU General Public License (V3). See [License](LICENSE) for more information.