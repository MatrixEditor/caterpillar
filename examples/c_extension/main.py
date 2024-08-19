# Just import the type as usual after "pip install ."
from example._example import ExampleCAtom

# NOTE: In this example wwe just print the object and don't
# show any additional implementation of packing or unpacking
# data.
obj = ExampleCAtom(5)
print(obj) # <ExampleCAtom 5>