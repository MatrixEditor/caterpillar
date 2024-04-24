from caterpillar._core import intatom, unpack

print(unpack(b"\x01", intatom(1)))