from caterpillar.py import Bytes, CTX_STREAM, Chain, Context, FieldStruct, pack, unpack


class SuffixTransform(FieldStruct[bytes, bytes]):
    def __init__(self, suffix: bytes):
        self.suffix: bytes = suffix
        self.events: list[tuple[str, bytes]] = []

    def __type__(self):
        return bytes

    def __size__(self, context):
        return 1

    def unpack_single(self, context):
        data = context[CTX_STREAM].read()
        self.events.append(("unpack", data))
        return data + self.suffix

    def pack_single(self, obj, context):
        self.events.append(("pack", obj))
        assert obj.endswith(self.suffix)
        context[CTX_STREAM].write(obj[: -len(self.suffix)])


def test_chain_unpacks_head_to_tail_and_packs_tail_to_head():
    one = SuffixTransform(b"1")
    two = SuffixTransform(b"2")
    chain = Chain(Bytes(1), one, two)

    assert unpack(chain, b"Atrailing") == b"A12"
    assert one.events == [("unpack", b"A")]
    assert two.events == [("unpack", b"A1")]

    one.events.clear()
    two.events.clear()

    assert pack(b"A12", chain) == b"A"
    assert two.events == [("pack", b"A12")]
    assert one.events == [("pack", b"A1")]


def test_and_operator_appends_to_existing_chain_in_order():
    one = SuffixTransform(b"1")
    two = SuffixTransform(b"2")
    chain = Chain(Bytes(1), one)

    returned = chain & two

    assert returned is chain
    assert unpack(chain, b"Z") == b"Z12"


def test_chain_type_and_size_are_taken_from_tail_and_head():
    one = SuffixTransform(b"1")
    chain = Chain(Bytes(1), tail=one)

    assert chain.head.__class__ is Bytes
    assert chain.tail is one
    assert chain.__type__() is bytes
    assert chain.__size__(Context()) == 1


def test_left_operand_prepends_when_right_operand_is_chain():
    prefix = SuffixTransform(b"P")
    suffix = SuffixTransform(b"S")
    chain = Chain(Bytes(1), suffix)

    combined = prefix & chain

    assert combined._elements[0] is prefix
    assert combined._elements[1].__class__ is Bytes
