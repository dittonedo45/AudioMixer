import fobject
import sys

class Format(fobject.Format):
    def __init__(s, *a, **kw):
        s.args=a
        (fobject.Format).__init__(s, *a, *kw)
        pass
    def _get_packet(s):
        while True:
            try:
                yield s.get_packet ()
            except EOFError:
                break
    def __iter__(s):
        for i in s._get_packet ():
            yield s.send_frame(i)
            try:
                while True:
                    yield s.send_frame(None)
            except EOFError:
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

for i in zip(*map (lambda x: Format(x), sys.argv[1:])):
    print(i)
