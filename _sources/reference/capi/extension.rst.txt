.. _reference_capi-extension:

***************
Using the C API
***************

This documentation provides a step-by-step guide for extending Caterpillar using its C API. The example provided demonstrates
how to create a C extension module named :code:`_example` integrated into the :code:`example` library. This guide covers the
setup of the build system using CMake and the implementation of the C extension module.

Before proceeding, ensure you have the following tools installed:

* CMake
* Python (with development headers)
* Obviously :code:`caterpillar`

Assuming you are using `scikit-build <https://scikit-build-core.readthedocs.io/en/stable/getting_started.html)>`_ to write
your extension, the following project structure applies:

.. code-block:: txt

    example-extension
    ├── CMakeLists.txt
    ├── pyproject.toml
    └── src
        ├── example/
        │   └── /* put python sources here */
        └── _example.c

The :code:`CMakeLists.txt` file configures the build system for the C extension module. Here's the content of an example
configuration:

.. code-block:: cmake
    :linenos:

    cmake_minimum_required(VERSION 3.15...3.26)
    project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

    # Setup Python Development Module
    find_package(
        Python
        COMPONENTS Interpreter Development.Module
        REQUIRED)

    # Either setup the include directory manually or use caterpillar directly
    set(CP_INCLUDE_DIR "...")
    # or
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m caterpillar --include-dir
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE CP_INCLUDE_DIR
    )

    # Setup the C extension module
    python_add_library(
        _example       # module name
        MODULE

        src/_example.c # source files

        WITH_SOABI
    )

    # setup include directories
    target_include_directories(
        _example
        PRIVATE
        ${CP_INCLUDE_DIR}
    )

    # install extension
    install(
        TARGETS _example
        DESTINATION example # use '.' to install directly without parent package
    )


The :code:`src/_example.c` file contains the implementation of the C extension module.
To define a custom CAtom, please refer to *work in progress*. There will be only one
important line when creating the custom module:

.. code-block:: c

    #include "caterpillar/caterpillar.h"

    PyMODINIT_FUNC
    PyInit__example(void) {
        PyObject *m;

        import_caterpillar(); // import and setup API

        /* create and setup module */
        // ...
        return m;
    }

Install the created extension module using scikit-build:

.. code-block:: bash

    pip install -v .

.. hint::
    The `c_extension <https://github.com/MatrixEditor/caterpillar/tree/master/examples/c_extension>`_ directory
    contains an example extension written in C.