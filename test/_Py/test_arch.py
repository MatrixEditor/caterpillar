import sys

from caterpillar.py import (
    Arch,
    Field,
    f,
    intptr,
    pack,
    sizeof,
    struct,
    system_arch,
    uint8,
    unpack,
    uintptr,
    x86,
    x86_64,
)


# --------------------------------------------------------------------------- #
# architecture descriptors
# --------------------------------------------------------------------------- #
def test_common_arch_instances_expose_pointer_bit_widths():
    assert x86 == Arch("x86", 32)
    assert x86_64 == Arch("x86-64", 64)
    assert x86.ptr_size // 8 == 4
    assert x86_64.ptr_size // 8 == 8


def test_default_system_arch_matches_python_word_size():
    expected = 64 if sys.maxsize > 2**32 else 32

    assert system_arch.ptr_size == expected
    assert isinstance(system_arch.name, str)
    assert system_arch.name


# --------------------------------------------------------------------------- #
# pointer-sized fields
# --------------------------------------------------------------------------- #
def test_root_arch_controls_unsigned_pointer_width():
    field = Field(uintptr)

    data32 = pack(0x01020304, field, arch=x86)
    data64 = pack(0x0102030405060708, field, arch=x86_64)

    assert data32 == bytes.fromhex("04030201")
    assert data64 == bytes.fromhex("0807060504030201")
    assert unpack(field, data32, arch=x86) == 0x01020304
    assert unpack(field, data64, arch=x86_64) == 0x0102030405060708


def test_root_arch_controls_signed_pointer_width():
    field = Field(intptr)

    assert pack(-2, field, arch=x86) == (-2).to_bytes(4, "little", signed=True)
    assert pack(-2, field, arch=x86_64) == (-2).to_bytes(8, "little", signed=True)


def test_default_arch_controls_pointer_width():
    field = Field(uintptr)

    assert len(pack(1, field)) == system_arch.ptr_size // 8


def test_struct_arch_controls_pointer_field_pack_width():
    @struct(arch=x86)
    class Ptr32:
        tag: f[int, uint8]
        ptr: f[int, uintptr]

    obj = Ptr32(0xAA, 0x01020304)

    assert sizeof(Ptr32) == 5
    assert pack(obj) == bytes.fromhex("aa04030201")
