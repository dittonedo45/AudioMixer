import fobject

class Format(fobject.Format):
    def __init__(s, *a, **kw):
        s.args=a
        (fobject.Format).__init__(s, *a, *kw)
        pass
    def __repr__(s):
        return "AVFormat({0!r})".format(s.args[0])
    pass
def args():
    import sys
    while True:
        yield from iter(sys.argv[1:])
    pass
import asyncio
async def ugh():
    try:
        for i in args():
            j=Format(i)
            await asyncio.sleep(0.1)
            print(j)
            pass
    except Exception:
        print(len(x));
        pass
    pass

#asyncio.run(ugh())
print(dir(fobject))
