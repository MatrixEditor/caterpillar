# Copyright (C) MatrixEditor 2023-2026
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# pyright: reportAny=false, reportExplicitAny=false, reportPrivateUsage=false
from tempfile import TemporaryFile
from io import BytesIO, IOBase
from collections import OrderedDict
from shutil import copyfileobj
from typing import Any
from typing_extensions import (
    overload,
    Buffer,
)

from caterpillar.byteorder import (
    O_DEFAULT_ARCH,
    O_DEFAULT_ENDIAN,
    LittleEndian,
    system_arch,
)
from caterpillar.shared import ATTR_PACK, getstruct, hasstruct
from caterpillar.context import O_CONTEXT_FACTORY, CTX_STREAM, Context
from caterpillar.exception import DynamicSizeError
from caterpillar.shared import MODE_PACK, MODE_UNPACK
from caterpillar.abc import (
    _ContainsStruct,
    _OT,
    _IT,
    _SupportsPack,
    _StreamType,
    _SupportsUnpack,
    _SupportsSize,
    _EndianLike,
    _ArchLike,
)


@overload
def pack(
    obj: _ContainsStruct[_IT, _OT],
    struct: None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwargs: Any,
) -> bytes: ...
@overload
def pack(
    # fallback to allow arbitrary objects
    obj: object,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> bytes: ...
@overload
def pack(
    obj: _IT,
    struct: _SupportsPack[_IT],
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwargs: Any,
) -> bytes: ...
@overload
def pack(
    obj: _IT,
    # support arbitrary struct types
    struct: type[_IT],
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwargs: Any,
) -> bytes: ...
def pack(
    obj: _IT | _ContainsStruct[_IT, _OT],
    struct: _SupportsPack[_IT] | type[_IT] | _ContainsStruct[_IT, _OT] | None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwargs: Any,
) -> bytes:
    """
    Pack an object into a bytes buffer using the specified struct.

    :param obj: The object to pack.
    :param struct: The struct to use for packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :return: The packed bytes.
    """
    buffer = BytesIO()
    pack_into(  # pyright: ignore[reportCallIssue]
        obj,
        buffer,
        struct,  # pyright: ignore[reportArgumentType]
        order=order,
        arch=arch,
        use_tempfile=use_tempfile,
        as_field=as_field,
        **kwargs,
    )
    return buffer.getvalue()


@overload
def pack_into(
    obj: _ContainsStruct[_IT, _OT],
    buffer: _StreamType,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    fill: int | bytes | str | None = None,
    **kwds: Any,
) -> None: ...
@overload
def pack_into(
    obj: object,
    buffer: _StreamType,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    fill: int | bytes | str | None = None,
    **kwds: Any,
) -> None: ...
@overload
def pack_into(
    obj: _IT,
    buffer: _StreamType,
    struct: _SupportsPack[_IT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    fill: int | bytes | str | None = None,
    **kwds: Any,
) -> None: ...
@overload
def pack_into(
    obj: _IT,
    buffer: _StreamType,
    struct: type[_IT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    fill: int | bytes | str | None = None,
    **kwds: Any,
) -> None: ...
@overload
def pack_into(
    obj: _IT,
    buffer: _StreamType,
    struct: _ContainsStruct[_IT, _OT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    fill: int | bytes | str | None = None,
    **kwds: Any,
) -> None: ...
def pack_into(
    obj: _IT | _ContainsStruct[_IT, _OT],
    buffer: _StreamType,
    struct: type[_IT] | _ContainsStruct[_IT, _OT] | _SupportsPack[_IT] | None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    fill: int | bytes | str | None = None,
    **kwds: Any,
) -> None:
    """
    Pack an object into the specified buffer using the specified struct.

    This function serializes an object (`obj`) into a given buffer, using
    a struct to define how the object should be packed. Optionally, the
    function can handle temporary files for packing, use a `Field` wrapper
    around the struct, and support additional keyword arguments. The packed
    data is written to the `buffer`.

    Example 1: Packing an object into a bytes buffer

    >>> buffer = BytesIO()
    >>> my_obj = SomeObject()  # Assume SomeObject is a valid object to be packed
    >>> pack_into(my_obj, buffer, struct=SomeStruct())  # Using a specific struct
    >>> buffer.getvalue()
    b"..."

    Example 2: Packing into a file-like stream (e.g., file)

    >>> with open('packed_data.bin', 'wb') as f:
    ...     pack_into(my_obj, f, struct=SomeStruct())  # Pack into a file

    Example 3: Using `as_field` to wrap the struct in a Field before packing

    >>> buffer = BytesIO()
    >>> pack_into(42, buffer, struct=uint8, as_field=True)
    >>> buffer.getvalue()
    b"\\x2a"

    :param obj: The object to pack (could be a plain object or a structure-like object).
    :param buffer: The buffer to pack the object into (a writable stream such as `BytesIO` or a file).
    :param struct: The struct to use for packing. If not specified, will infer from `obj`.
    :param use_tempfile: Whether to use a temporary file for packing (experimental).
    :param as_field: Whether to wrap the struct in a `Field` before packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :raises TypeError: If no `struct` is specified and cannot be inferred from the object.
    """
    # fmt: off
    offsets: OrderedDict[int, bytes] = OrderedDict()
    # NOTE: we don't have to set _root here because the default root context
    # will be this instance.
    context = (O_CONTEXT_FACTORY.value or Context)(
        _parent=None,
        _path="<root>",
        _pos=0,
        _offsets=offsets,
        _is_seq=False,
        _order=order or O_DEFAULT_ENDIAN.value or LittleEndian,
        _arch=arch or O_DEFAULT_ARCH.value or system_arch,
        mode=MODE_PACK,
        **kwds,
    )
    if struct is None:
        struct = getstruct(obj)
    elif as_field:
        from caterpillar.fields import Field
        struct = Field(struct)  # pyright: ignore[reportArgumentType]
    elif hasstruct(struct):
        struct = getstruct(struct)

    if struct is None:
        raise TypeError("struct must be specified")

    if not hasattr(struct, ATTR_PACK):
        raise TypeError(
            f"pack* called with an unknown struct type ({type(struct)}) - "
            + "no __pack__ defined!"
        )

    prev_order = O_DEFAULT_ENDIAN.value
    prev_arch = O_DEFAULT_ARCH.value
    if order:
        O_DEFAULT_ENDIAN.value = order
    if arch:
        O_DEFAULT_ARCH.value = prev_arch
    try:
        start: int = 0
        fill_pat: bytes = b"\x00"
        match fill:
            case str():
                fill_pat = fill.encode()
            case bytes():
                fill_pat = bytes(fill)
            case int():
                fill_pat = bytes([fill])
            case None:
                fill_pat = b"\x00"
            case _:
                raise TypeError("Invalid fill type!")

        if use_tempfile:
            # NOTE: this implementation is exprimental - use this option with caution.
            stream = TemporaryFile()

        else:
            # Default implementation: We use an in-memory buffer to store all packed
            # elements and then apply all offset-packed objects.
            stream = BytesIO()

        with stream: # <-- closes tempfile automatically
            context[CTX_STREAM] = stream
            struct.__pack__(obj, context) # pyright: ignore

            _buf_data = bytearray()
            _ = stream.seek(0)
            if len(offsets) != 0:
                for offset, value in offsets.items():
                    _ = stream.seek(start)
                    content_data = stream.read(offset - start)

                    buffer.write(content_data)
                    # adjust filler automatically
                    start += len(content_data)
                    if start < offset:
                        pad_length = offset - start
                        if pad_length % len(fill_pat) != 0:
                            raise ValueError(f"invalid pattern length. Fill pattern does not fit into {pad_length} bytes")

                        count: int = pad_length // len(fill_pat)
                        buffer.write(fill_pat * count)
                        start += pad_length

                    buffer.write(value)
                    start += len(value)
            else:
                copyfileobj(stream, buffer)
    finally:
        O_DEFAULT_ENDIAN.value = prev_order
        O_DEFAULT_ARCH.value = prev_arch


@overload
def pack_file(
    obj: _ContainsStruct[_IT, _OT],
    filename: str,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
@overload
def pack_file(
    obj: object,
    filename: str,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
@overload
def pack_file(
    obj: _IT,
    filename: str,
    struct: _SupportsPack[_IT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
@overload
def pack_file(
    obj: _IT,
    filename: str,
    struct: type[_IT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
@overload
def pack_file(
    obj: _IT,
    filename: str,
    struct: _ContainsStruct[_IT, _OT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
def pack_file(
    obj: _IT | _ContainsStruct[_IT, _OT],
    filename: str,
    struct: _SupportsPack[_IT] | type[_IT] | _ContainsStruct[_IT, _OT] | None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> None:
    """
    Pack an object into a file using the specified struct.

    :param obj: The object to pack.
    :param filename: The name of the file to write to.
    :param struct: The struct to use for packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :return: None
    """
    with open(filename, "w+b") as fp:
        pack_into(  # pyright: ignore[reportCallIssue]
            obj,
            fp,
            struct,  # pyright: ignore[reportArgumentType]
            use_tempfile=use_tempfile,
            as_field=as_field,
            order=order,
            arch=arch,
            **kwds,
        )


@overload
def unpack(
    struct: _ContainsStruct[_IT, _OT],
    buffer: Buffer | _StreamType,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
@overload
def unpack(
    struct: _SupportsUnpack[_OT],
    buffer: Buffer | _StreamType,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
@overload
def unpack(
    struct: type[_OT],
    buffer: Buffer | _StreamType,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
def unpack(
    struct: type[_OT] | _SupportsUnpack[_OT] | _ContainsStruct[_IT, _OT],
    buffer: Buffer | _StreamType,
    /,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT:
    """
    Unpack an object from a bytes buffer or stream using the specified struct.

    This function takes a `struct` that defines how data should be unpacked,
    a `buffer` (either bytes or a stream) containing the serialized data, and
    returns the unpacked object. If `as_field` is set to True, the `struct` is
    wrapped by a `Field`. Additional keyword arguments are passed to the root
    context as attributes.

    Example:

    >>> buffer = b'\\x00\\x01\\x02\\x03'
    >>> struct = SomeStruct()
    >>> unpack(struct, buffer)
    ...

    :param struct: The struct to use for unpacking (could be a `SupportsUnpack` or `ContainsStruct` object).
    :param buffer: The bytes buffer or stream to unpack from.
    :param as_field: Whether to wrap the struct in a `Field` transformer before unpacking.
    :param kwds: Additional keyword arguments to pass to the unpack function.

    :return: The unpacked object, which is the result of calling `struct.__unpack__(context)`.

    :raises TypeError: If the `struct` is not a valid struct instance.
    """
    # fmt: off
    # prepare the data stream
    stream = buffer if isinstance(buffer, IOBase) else BytesIO(buffer)
    context = (O_CONTEXT_FACTORY.value or Context)(
        _path="<root>",
        _parent=None,
        _io=stream,
        _pos=0,
        _is_seq=False,
        _order=order or O_DEFAULT_ENDIAN.value or LittleEndian,
        _arch=arch or O_DEFAULT_ARCH.value or system_arch,
        mode=MODE_UNPACK,
        **kwds,
    )
    if as_field:
        from caterpillar.fields import Field
        struct = Field(struct)  # pyright: ignore[reportArgumentType]
    elif hasstruct(struct):
        struct = getstruct(struct)

    if not isinstance(struct, _SupportsUnpack):
        raise TypeError(f"{type(struct).__name__} is not a valid struct instance!")

    prev_order = O_DEFAULT_ENDIAN.value
    prev_arch = O_DEFAULT_ARCH.value
    if order:
        O_DEFAULT_ENDIAN.value = order
    if arch:
        O_DEFAULT_ARCH.value = arch

    try:
        return struct.__unpack__(context)
    finally:
        O_DEFAULT_ARCH.value = prev_arch
        O_DEFAULT_ENDIAN.value = prev_order


@overload
def unpack_file(
    struct: _ContainsStruct[_IT, _OT],
    filename: str,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
@overload
def unpack_file(
    struct: _SupportsUnpack[_OT],
    filename: str,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
@overload
def unpack_file(
    struct: type[_OT],
    filename: str,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
def unpack_file(
    struct: type[_OT] | _SupportsUnpack[_OT] | _ContainsStruct[_IT, _OT],
    filename: str,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
):
    """
    Unpack an object from a file using the specified struct.

    :param struct: The struct to use for unpacking.
    :param filename: The name of the file to read from.
    :param kwds: Additional keyword arguments to pass to the unpack function.

    :return: The unpacked object.
    """
    with open(filename, "rb") as fp:
        return unpack(struct, fp, as_field=as_field, arch=arch, order=order, **kwds)


@overload
def sizeof(obj: _SupportsSize, **kwds: Any) -> int: ...
@overload
def sizeof(obj: _ContainsStruct, **kwds: Any) -> int: ...
@overload
def sizeof(obj: type, **kwds: Any) -> int: ...
def sizeof(obj: _SupportsSize | _ContainsStruct | type, **kwds: Any) -> int:
    context = (O_CONTEXT_FACTORY.value or Context)(_parent=None, _path="<root>", **kwds)
    struct_ = obj
    if hasstruct(struct_):
        struct_ = getstruct(struct_)

    if not isinstance(struct_, _SupportsSize):
        raise TypeError(f"{type(struct_).__name__} does not support size calculation!")

    size = struct_.__size__(context)
    if not isinstance(size, int):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise DynamicSizeError(f"Struct {struct_} is using a dynamic size ", context)
    return size
