from construct import *

d = Struct(
    "count" / Int32ul,
    "items"
    / Array(
        this.count,
        Struct(
            "num1" / Int8ul,
            "num2" / Int24ul,
            "flags"
            / BitStruct(
                "bool1" / Flag,
                "num4" / BitsInteger(3),
                Padding(4),
            ),
            "fixedarray1" / Array(3, Int8ul),
            "name1" / CString("utf8"),
            "name2" / PascalString(Int8ul, "utf8"),
        ),
    ),
)
d_compiled = d.compile()


# Create the blob with:
# data = d.build(
#     dict(
#         count=1000,
#         items=[
#             dict(
#                 num1=0,
#                 num2=0,
#                 flags=dict(bool1=True, num4=0),
#                 fixedarray1=[0, 0, 0],
#                 name1="...",
#                 name2="...",
#             )
#             for i in range(1000)
#         ],
#     )
# )
# with open("blob", "wb") as f:
#     f.write(data)

if __name__ == "__main__":
    import sys
    import timeit

    try:
        from rich import print
    except ImportError:
        pass

    with open(sys.argv[1], "rb") as fp:
        data = fp.read()

    obj = d.parse(data)
    time = timeit.timeit(lambda: d.parse(data), number=1000) / 1000
    time_compiled = timeit.timeit(lambda: d_compiled.parse(data), number=1000) / 1000
    print("[bold]Parsing measurements:[/]")
    print(f"[bold]default[/]  {time:.10f} sec/call")
    print(f"[bold]compiled[/] {time_compiled:.10f} sec/call\n")

    btime = timeit.timeit(lambda: d.build(obj), number=1000) / 1000
    btime_compiled = timeit.timeit(lambda: d_compiled.build(obj), number=1000) / 1000

    print("[bold]Building measurements:[/]")
    print(f"[bold]default[/]  {btime:.10f} sec/call")
    print(f"[bold]compiled[/] {btime_compiled:.10f} sec/call")
