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
            yield  s, s.send_frame(i)
            try:
                while True:
                    yield s, s.send_frame(None)
            except EOFError:
                pass
    def __repr__(s):
        return "AVFormat({0!r})".format(s.args[0])
    pass
def args():
    import sys
    yield from iter(sys.argv[1:])
    pass
import asyncio
import random
async def rand(l):
    return l[random.randint(0,len(l)-1)]

async def Deck(tracks):
    while True:
        x=Format(await rand(tracks))
        await asyncio.sleep(0)
        for i in x:
            yield x, i
            await asyncio.sleep (0)

async def deck1(x, cb, index):
        y=Deck(x)
        await asyncio.sleep(0)
        async for x, i in y:
            cb(i, index)
            await asyncio.sleep(0)


def just(i, x):
    assert(type(x)==int)
    assert(x>0)
    y=iter (i)
    while (x:=x-1)>=0:
        yield next(y)

async def main (cb, *args):
    await asyncio.gather(*map(lambda x: deck1(list(args), cb, x), range(2)))

def cbb(x, index):
    (self, frame)=x
    fobject.get_frame(frame, index)
asyncio.run (main(cbb, *args()))
