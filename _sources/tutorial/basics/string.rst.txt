.. _tutorial-basics-strings:

************
String Types
************

In binary file formats, string handling can be complex due to varying lengths,
encodings, and termination methods. *Caterpillar* provides several specialized
string types to manage these intricacies with ease.

Default Strings
---------------

The standard type for regular string handling, requiring you to specify a fixed
or dynamic length.

.. tab-set::

    .. tab-item:: Python

        >>> s = String(100 or this.length) # static integer or context lambda

    .. tab-item:: Caterpillar C

        >>> # takes static length, context lambda or ... for greedy parsing
        >>> s = string(100)


CString
-------

The :code:`CString` type is used to handle strings that end with a null byte. It
extends beyond simple C-style strings. Here's how you might define a structure using a
:code:`CString`:

.. tab-set::

    .. tab-item:: Python

        .. code-block:: python
            :caption: The `tEXt <https://www.w3.org/TR/png/#11tEXt>`_ chunk structure

            from caterpillar.py import *
            from caterpillar.shortcuts import lenof

            @struct
            class TEXTChunk:
                # dynamic sized string that ends with a null-byte
                keyword: CString(encoding="ISO-8859-1")
                # static sized string based on the current context. some notes:
                #   - parent.length is the current chunkt's length
                #   - lenof(...) is the runtime length of the context variable
                #   - 1 because of the extra null-byte that is stripped from keyword
                text: CString(encoding="ISO-8859-1", length=parent.length - lenof(this.keword) - 1)

    .. tab-item:: Caterpillar C

        .. code-block:: python
            :caption: The `tEXt` chunk structure

            from caterpillar.c import *                 # <-- main difference
            from caterpillar.shortcuts import lenof
            # NOTE: lenof works here, because Caterpillar C's Context implements
            # the 'Context Protocol'.

            parent = ContextPath("parent.obj")
            this = ContextPath("obj")

            @struct
            class TEXTChunk:
                # dynamic sized string that ends with a null-byte
                keyword: cstring(encoding="ISO-8859-1")
                # static sized string based on the current context. some notes:
                #   - parent.length is the current chunkt's length
                #   - lenof(...) is the runtime length of the context variable
                #   - 1 because of the extra null-byte that is stripped from keyword
                text: cstring(encoding="ISO-8859-1", length=parent.length - lenof(this.keword) - 1)

.. admonition:: Challenge

    Try implementing the `iTXt <https://www.w3.org/TR/png/#11iTXt>`_ chunk from the PNG format.
    This chunk uses a combination of strings and fixed-length fields. Here's a possible solution:

    .. dropdown:: Solution
        :icon: check

        This solution serves as an example and isn't the only way to approach it!

        .. tab-set::

            .. tab-item:: Python

                .. code-block:: python
                    :linenos:

                    @struct
                    class ITXTChunk:
                        keyword: CString(encoding="utf-8")
                        compression_flag: uint8
                        # we actually don't need an Enum here
                        compression_method: uint8
                        language_tag: CString(encoding="ASCII")
                        translated_keyword: CString(encoding="utf-8")
                        # length is calculated with parent.length - len(keyword)+len(b"\x00") - ...
                        text: CString(
                            encoding="utf-8",
                            length=parent.length - lenof(this.translated_keyword) - lenof(this.keyword) - 5,
                        )

            .. tab-item:: Caterpillar C

                .. code-block:: python
                    :linenos:

                    from caterpillar.c import *                 # <-- main difference
                    from caterpillar.shortcuts import lenof

                    parent = ContextPath("parent.obj")
                    this = ContextPath("obj")

                    @struct
                    class ITXTChunk:
                        keyword: cstring() # default encoding is "utf-8"
                        compression_flag: u8
                        # we actually don't need an Enum here
                        compression_method: u8
                        language_tag: cstring(encoding="ASCII")
                        translated_keyword: cstring(...) # explicit greedy parsing
                        # length is calculated with parent.length - len(keyword)+len(b"\x00") - ...
                        text: cstring(
                            parent.length - lenof(this.translated_keyword) - lenof(this.keyword) - 5,
                        )

You can also customize the string's termination character if needed:

.. tab-set::

    .. tab-item:: Python

        >>> struct = CString(pad="\x0A")

    .. tab-item:: Caterpillar C

        >>> s = cstring(sep="\x0A")


Pascal Strings
--------------

The :class:`~caterpillar.py.Prefixed` class implements Pascal strings, where the
length of the string is prefixed to the actual data. This is useful when dealing
with raw bytes or strings with a length indicator.

.. tab-set::

    .. tab-item:: Python

        >>> s = Prefixed(uint8, encoding="utf-8")
        >>> pack("Hello, World!", s, as_field=True)
        b'\rHello, World!'
        >>> unpack(s, _, as_field=True)
        'Hello, World!'

    .. tab-item:: Caterpillar C

        >>> s = pstring(u8)
        >>> pack("Hello, World!", s)
        b'\rHello, World!'
        >>> unpack(_, s)
        'Hello, World!'
