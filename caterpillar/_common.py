# Copyright (C) MatrixEditor 2023
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
import itertools

from typing import List, Any, Union, Iterable

from caterpillar.abc import _GreedyType, _ContextLike, isgreedy, _StreamType, isprefixed
from caterpillar.context import (
    Context,
    CTX_PATH,
    CTX_FIELD,
    CTX_POS,
    CTX_INDEX,
    CTX_OBJECT,
    CTX_STREAM,
)
from caterpillar.options import F_SEQUENTIAL
from caterpillar.exception import Stop, StructException, InvalidValueError


class WithoutFlag:
    def __init__(self, context: _ContextLike, flag) -> None:
        self.context = context
        self.field = context[CTX_FIELD]
        self.flag = flag

    def __enter__(self) -> None:
        self.field ^= self.flag

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.field |= self.flag
        # We have to apply the right field as instance of the Field class
        # might set their own value into the context.
        self.context[CTX_FIELD] = self.field


def unpack_seq(context: _ContextLike, unpack_one) -> List[Any]:
    """Generic function to unpack sequenced elements.

    :param stream: the input stream
    :type stream: _StreamType
    :param context: the current context
    :type context: _ContextLike
    :return: a list of unpacked elements
    :rtype: List[Any]
    """
    stream = context[CTX_STREAM]
    field = context[CTX_FIELD]
    assert field and field.is_seq()

    length: Union[int, _GreedyType] = field.length(context)
    base_path = context[CTX_PATH]
    # Special elements '_index' and '_length' can be referenced within
    # the new context. The '_pos' attribute will be adjusted automatically.
    values = []  # always list (maybe add factory)
    seq_context = Context(
        _parent=context,
        _io=stream,
        _length=length,
        _lst=values,
        _field=field,
        _obj=context.get(CTX_OBJECT),
    )
    greedy = isgreedy(length)
    prefixed = isprefixed(length)
    seq_context[CTX_POS] = stream.tell()
    if prefixed:
        # We have to temporarily remove the array status from the parsing field
        with WithoutFlag(context, F_SEQUENTIAL):
            field.amount = 1
            new_length = length.start.__unpack__(context)
            field.amount, length = length, new_length

        if not isinstance(length, int):
            raise InvalidValueError(
                f"Prefix struct returned non-integer: {length!r}", context
            )

    for i in range(length) if not greedy else itertools.count():
        try:
            seq_context[CTX_PATH] = ".".join([base_path, str(i)])
            seq_context[CTX_INDEX] = i
            values.append(unpack_one(seq_context))
            seq_context[CTX_POS] = stream.tell()

            # NOTE: we introduce this check to reduce time when unpacking
            # a greedy range of elements.
            if greedy and iseof(stream):
                break
        except Stop:
            break
        except Exception as exc:
            if greedy:
                break
            raise StructException(str(exc), context) from exc
    return values


def pack_seq(seq: List[Any], context: _ContextLike, pack_one) -> None:
    """Generic function to pack sequenced elements.

    :param seq: the iterable of elements
    :type seq: Iterable
    :param stream: the output stream
    :type stream: _StreamType
    :param context: the current operation context
    :type context: _ContextLike
    :raises InvalidValueError: if the input object is not iterable
    """
    stream = context[CTX_STREAM]
    field = context[CTX_FIELD]
    base_path = context[CTX_PATH]
    # Treat the 'obj' as a sequence/iterable
    if not isinstance(seq, Iterable):
        raise InvalidValueError(f"Expected iterable sequence, got {type(seq)}", context)

    # REVISIT: when to use field.length(context)
    count = len(seq)
    length = field.amount
    if isprefixed(length):
        struct = length.start
        # We have to temporatily alter the field's values,
        with WithoutFlag(context, F_SEQUENTIAL):
            field.amount = 1
            struct.__pack__(count, context)
            field.amount = length

    # Special elements '_index' and '_length' can be referenced within
    # the new context. The '_pos' attribute will be adjusted automatically.
    seq_context = Context(
        _parent=context,
        _io=stream,
        _length=count,
        _field=field,
        _obj=context.get(CTX_OBJECT),
    )
    seq_context[CTX_POS] = stream.tell()
    for i, elem in enumerate(seq):
        # The path will contain an additional hint on what element is processed
        # at the moment.
        seq_context[CTX_INDEX] = i
        seq_context[CTX_PATH] = ".".join([base_path, str(i)])
        seq_context[CTX_OBJECT] = elem
        pack_one(elem, seq_context)
        seq_context[CTX_POS] = stream.tell()


def iseof(stream: _StreamType) -> bool:
    """
    Check if the stream is at the end of the file.

    :param _StreamType stream: The input stream.
    :return: True if the stream is at the end of the file, False otherwise.
    :rtype: bool
    """
    pos = stream.tell()
    eof = not stream.read(1)
    stream.seek(pos)
    return eof