import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar.c import c_Arch, c_Endian

    def testc_arch_init():
        c_Arch("name", 32)
        with pytest.raises(TypeError):
            c_Arch()

    def testc_endian_init():
        c_Endian("name", ord("!"))
        with pytest.raises(TypeError):
            c_Endian()

    def testc_arch_repr():
        a = c_Arch("name", 32)
        assert repr(a) == "<Arch 'name' x32>"

    def testc_endian_repr():
        le = c_Endian("name", ord("<"))
        assert repr(le) == "<le>"

        be = c_Endian("name", ord(">"))
        net = c_Endian("name", ord("!"))
        assert repr(be) == "<be>" and repr(net) == "<be>"

        ne = c_Endian("name", ord("="))
        assert repr(ne) == "<native-endian>"

        custom = c_Endian("Custom", ord("/"))
        assert repr(custom) == "<ByteOrder: Custom ch='/'>"