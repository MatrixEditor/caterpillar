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

from caterpillar.abc import _GreedyType, _StreamType, _ContextLike, isgreedy
from caterpillar.context import Context
from caterpillar.exception import Stop, StructException


def unpack_seq(stream: _StreamType, context: _ContextLike, unpack_one) -> List[Any]:
    """Generic function to unpack sequenced elements.

    :param stream: the input stream
    :type stream: _StreamType
    :param context: the current context
    :type context: _ContextLike
    :return: a list of unpacked elements
    :rtype: List[Any]
    """
    field = context._field
    assert field and field.is_seq()

    length: Union[int, _GreedyType] = field.length(context)
    base_path = context._path
    # Special elements '_index' and '_length' can be referenced within
    # the new context. The '_pos' attribute will be adjusted automatically.
    values = []  # always list (maybe add factory)
    seq_context = Context(
        _parent=context, _io=stream, _length=length, _lst=values, _field=field
    )
    greedy = isgreedy(length)
    seq_context._pos = stream.tell()
    for i in range(length) if not greedy else itertools.count():
        try:
            seq_context._path = ".".join([base_path, str(i)])
            seq_context._index = i
            values.append(unpack_one(stream, seq_context))
            seq_context._pos = stream.tell()
        except Stop:
            break
        except Exception as exc:
            if greedy:
                break
            raise StructException from exc
    return values


def pack_seq(
    seq: List[Any], stream: _StreamType, context: _ContextLike, pack_one
) -> None:
    """Generic function to pack sequenced elements.

    :param seq: the iterable of elements
    :type seq: Iterable
    :param stream: the output stream
    :type stream: _StreamType
    :param context: the current operation context
    :type context: _ContextLike
    :raises TypeError: if the input object is not iterable
    """
    field = context._field
    base_path = context._path
    # Treat the 'obj' as a sequence/iterable
    if not isinstance(seq, Iterable):
        raise TypeError(f"Expected iterable sequence, got {type(seq)}")

    # REVISIT: when to use field.length(context)
    count = len(seq)

    # Special elements '_index' and '_length' can be referenced within
    # the new context. The '_pos' attribute will be adjusted automatically.
    seq_context = Context(_parent=context, _io=stream, _length=count, _field=field)
    seq_context._pos = stream.tell()
    for i, elem in enumerate(seq):
        # The path will contain an additional hint on what element is processed
        # at the moment.
        seq_context._index = i
        seq_context._path = ".".join([base_path, str(i)])
        seq_context._obj = elem
        pack_one(elem, stream, seq_context)
        seq_context._pos = stream.tell()
