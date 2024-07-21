.. _installing:

************
Installation
************

*caterpillar* does not have a direct Python installation candidate. Therefore, you will need
to install it by providing the Git link. This library has no fixed dependencies, so it can run
out of the box.

There are several installation options you can use to install a desired part of the library. By
default, *caterpillar* ships with a native C extension and additional tools, that are using native
extensions too. AS not everyone wants to use C extensions, it is possible to install the library
without them:

.. code-block:: bash

    CP_DISABLE_NATIVE=TRUE \
    CP_DISABLE_TOOLS=TRUE \
    pip install git+https://github.com/MatrixEditor/caterpillar.git


.. note::
    If you clone the repository, don't forget to add `-e` to the installation via pip as
    it enables developer mode.


This project comes with packaging extras. Therefore, if you want to enable specific structs, you
have to install the corresponding extra. It can be done using pip again:

.. code-block:: bash

    pip install "caterpillar[$NAME]@git+https://github.com/MatrixEditor/caterpillar.git"

where :code:`$NAME` refers to

* `lzo`: for LZO compression support
* `crypt`: for extended encryption/decryption support
* `all`: to simply install all optional dependencies


.. tip::
    If you wish to contribute to this project, make sure you follow the :ref:`contribution`. This
    library is especially designed for Python 3.12 and prior versions are still subject to approval.