import pytest
import caterpillar
import io

if caterpillar.native_support():
    from caterpillar._C import AtOffset
    from caterpillar.py import Bytes, pack, unpack, sizeof, ctx

    # Offset initialization can be either done manually or by
    # using the '@' (matmul) operator on subclasses of BuiltinAtom.
    def testc_offset_init():
        atom = AtOffset(Bytes(1), 0)
        assert atom.is_number
        assert atom.whence == 0
        assert not atom.keep_pos

        # whence must be valid
        assert AtOffset(Bytes(1), 0, whence=io.SEEK_CUR).whence == 1
        with pytest.raises(ValueError):
            _ = AtOffset(Bytes(1), 0, whence=4)

    def testc_offset_type():
        atom = AtOffset(Bytes(1), 0)
        assert atom.__type__() is bytes

    def testc_offset_size():
        atom = AtOffset(Bytes(1), 0)
        assert sizeof(atom) == 1

    def testc_offset_pack():
        atom = AtOffset(Bytes(1), 0)
        assert pack(b"a", atom) == b"a"

        # offset may be a context lambda
        atom = AtOffset(Bytes(1), ctx._root.offset)
        assert pack(b"a", atom, offset=0) == b"a"

    def testc_offset_unpack():
        atom = AtOffset(Bytes(1), 0)
        assert unpack(atom, b"a") == b"a"

        # offset may be a context lambda
        atom = AtOffset(Bytes(1), ctx._root.offset)
        assert unpack(atom, b"a", offset=0) == b"a"
