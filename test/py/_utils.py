from caterpillar.shortcuts import pack, unpack

def _test_pack(obj, expected):
    data = pack(obj)
    assert data == expected, f"Invalid result data: {data!r} - expected {expected!r}"


def _test_unpack(struct_ty, data, expected):
    obj = unpack(struct_ty, data)
    assert obj == expected, f"Invalid result object: {obj!r} - expected {expected!r}"
