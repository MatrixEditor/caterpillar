from caterpillar._C import intatom, unpack

print(unpack(b"\x01", intatom(1)))