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

>>> # takes static length, context lambda or ... for greedy parsing
>>> s = String(100 or this.length) # static integer or context lambda


CString
-------

The :code:`CString` type is used to handle strings that end with a null byte. It
extends beyond simple C-style strings. Here's how you might define a structure using a
:code:`CString`:

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


.. admonition:: Challenge

    Try implementing the `iTXt <https://www.w3.org/TR/png/#11iTXt>`_ chunk from the PNG format.
    This chunk uses a combination of strings and fixed-length fields. Here's a possible solution:

    .. dropdown:: Solution
        :icon: check

        This solution serves as an example and isn't the only way to approach it!

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


You can also customize the string's termination character if needed:

>>> struct = CString(pad="\x0A")


Pascal Strings
--------------

The :class:`~caterpillar.py.Prefixed` class implements Pascal strings, where the
length of the string is prefixed to the actual data. This is useful when dealing
with raw bytes or strings with a length indicator.

>>> s = Prefixed(uint8, encoding="utf-8")
>>> pack("Hello, World!", s, as_field=True)
b'\rHello, World!'
>>> unpack(s, _, as_field=True)
'Hello, World!'

