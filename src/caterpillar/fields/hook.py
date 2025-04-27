# Copyright (C) MatrixEditor 2023-2025
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
from io import RawIOBase
from typing import Callable, Optional

from caterpillar.abc import _ContextLike
from caterpillar.context import CTX_STREAM

HookInit = Callable[[_ContextLike], None]
HookUpdate = Callable[[bytes, _ContextLike], Optional[bytes]]
HookRead = Callable[[bytes, _ContextLike], Optional[bytes]]
HookWrite = Callable[[bytes, _ContextLike], Optional[bytes]]
HookFinish = Callable[[_ContextLike], None]


class IOHook(RawIOBase):
    """
    A custom I/O stream wrapper that allows hooks to be installed for various
    stages of stream interaction, such as initialization, reading and writing.

    This class can be used to augment the functionality of an existing stream (e.g.,
    file streams, memory buffers, or network sockets) by attaching custom logic for
    handling data as it is read or written.

    :param io: The underlying I/O stream to which the hooks are applied.
    :type io: RawIOBase
    :param init: Optional hook function to be called during initialization.
    :type init: Optional[HookInit]
    :param update: Optional hook function to modify data before or after reading/writing.
    :type update: Optional[HookUpdate]
    :param read: Optional hook function to be applied to data after reading.
    :type read: Optional[HookRead]
    :param write: Optional hook function to be applied to data before writing.
    :type write: Optional[HookWrite]
    :param finish: Optional hook function to be called when the stream is finished.
    :type finish: Optional[HookFinish]
    """

    def __init__(
        self,
        io: RawIOBase,
        init: Optional[HookInit] = None,
        update: Optional[HookUpdate] = None,
        read: Optional[HookRead] = None,
        write: Optional[HookWrite] = None,
        finish: Optional[HookFinish] = None,
    ) -> None:
        # NOTE: no validation here if _io is valid, because
        # self.init will set it
        self._io = io
        self._init = init
        self._update = update
        self._read = read
        self._write = write
        self._finish = finish
        self._context = None

    def assert_context_set(self) -> None:
        """
        Ensures that the context has been set before any I/O operations are performed.

        :raises ValueError: If the context is not set.
        """
        if self._context is None:
            raise ValueError("Context is not set")

    def init(self, context: _ContextLike) -> None:
        """
        Initialize the I/O hook with the provided context. This triggers the
        `init` hook, if available, and sets up the context for subsequent operations.

        :param context: The context to be used for initializing the stream.
        :type context: _ContextLike
        """
        if self._init:
            self._init(context)
        self._context = context
        self._io = context[CTX_STREAM]
        self._context[CTX_STREAM] = self

    def finish(self, context: _ContextLike) -> None:
        """
        Finalize the I/O hook by calling the `finish` hook (if provided) and
        restoring the original I/O stream in the context.

        :param context: The context used during the finalization.
        :type context: _ContextLike
        """
        if self._finish:
            self._finish(context)

        context[CTX_STREAM] = self._io
        self._context = None

    def seekable(self) -> bool:
        """
        Checks if the underlying I/O stream is seekable.

        :return: True if the stream supports seeking, otherwise False.
        :rtype: bool
        """
        return self._io.seekable()

    def readable(self) -> bool:
        """
        Checks if the underlying I/O stream is readable.

        :return: True if the stream supports reading, otherwise False.
        :rtype: bool
        """
        return super().readable()

    def read(self, size: int = -1) -> bytes | None:
        """
        Read data from the stream, applying the optional hooks (if any).

        - The `update` hook, if provided, will be called to modify the data.
        - The `read` hook, if provided, will be called to further modify the data.

        :param size: The number of bytes to read, defaults to -1 (read until EOF).
        :type size: int
        :return: The read data, possibly modified by the hooks.
        :rtype: Union[bytes, None]
        """
        self.assert_context_set()
        data = self._io.read(size)
        if data is None:
            return

        if self._update:
            data = self._update(data, self._context) or data

        if self._read:
            data = self._read(data, self._context) or data

        return data

    def write(self, b: bytes, /) -> int | None:
        """
        Write data to the stream, applying the optional hooks (if any).

        - The `update` hook, if provided, will be called to modify the data before writing.
        - The `write` hook, if provided, will be called to modify the data before the final write operation.

        :param b: The data to write.
        :type b: bytes
        :return: The number of bytes written to the underlying stream.
        :rtype: Union[int, None]
        """
        self.assert_context_set()
        if self._update:
            b = self._update(b, self._context) or b

        if self._write:
            b = self._write(b, self._context) or b

        return self._io.write(b)

    def writable(self) -> bool:
        """
        Checks if the underlying I/O stream is writable.

        :return: True if the stream supports writing, otherwise False.
        :rtype: bool
        """
        return self._io.writable()

    def tell(self) -> int:
        """
        Returns the current position of the underlying stream.

        :return: The current position in the stream.
        :rtype: int
        """
        return self._io.tell()

    def seek(self, offset: int, whence: int = 0) -> int:
        """
        Move the cursor to a new position in the underlying stream.

        :param offset: The offset to move.
        :param whence: The reference point for the offset (default is 0, SEEK_SET).
        :return: The new position in the stream.
        :rtype: int
        """
        return self._io.seek(offset, whence)
