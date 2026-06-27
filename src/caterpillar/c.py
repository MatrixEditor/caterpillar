import caterpillar

if caterpillar.native_support():
    from caterpillar._C import *  # noqa
