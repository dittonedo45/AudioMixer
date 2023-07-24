import fobject
import sys
import asyncio
import random
import aiofiles
import typing

class Pac(typing.List):
    def append(self, *args):
        if (len(self)>5000):
            del self[:90]
        else:
            super().append(*args)

async def run(*args):
        loop=asyncio.get_running_loop ()
        return await loop.run_in_executor(None, *args)

class Format(fobject.Format):
    def __init__(s, *a, **kw):
        s.args=a
        (fobject.Format).__init__(s, *a, *kw)
        pass
    async def _get_packet(s):
        async def get_packet():
            return await run(s.get_packet)
        while True:
            try:
                yield await get_packet ()
            except fobject.EOF:
                return
    async def __aiter__(s):
        async for i in s._get_packet ():
            await asyncio.sleep(0)
            pkt=s.send_frame(i)
            if not pkt:
                continue
            yield s, pkt
            try:
                while True:
                    yield s, s.send_frame(None)
            except EOFError:
                pass
    def __repr__(s):
        return "AVFormat({0!r})".format(s.args[0])
    pass

def args():
    yield from iter(sys.argv[1:])
    pass

async def rand(l):
    loop=asyncio.get_running_loop()
    async def randint(*x):
        return await loop.run_in_executor (None, random.randint, *x)
    s=l[await randint(0,len(l)-1)]
    return s

async def Deck(tracks):
    while True:
        async def Format_(*x):
            return await run(Format, *x)
        try:
            x=await Format_(await rand(tracks))
        except SystemError as e:
                continue
        else:
            async for i in x:
                yield x, i
class Filter(fobject.Filter):
    def __init__(self, arg):
        fobject.Filter.__init__ (self, arg)
        self.dnc=asyncio.Semaphore(3)
    def get(self):
        return self.get_frame_from_sink ()
    def send(self, frame, index):
        self.send_frame_to_src(frame, index)
    async def write (self, frame, file):
        if not (isinstance(frame, (int))):
            for pkt in self.swallow (frame):
                file.write(pkt)
                file.flush ()
    async def ping_pong (main_filter, i, index, file):
        main_filter.send(i, index)
        frame=main_filter.get()
        await main_filter.write (frame, file)
class effects(object):
    def __init__(s, arg):
        s.filter=Filter(arg)
    async def change(s, arg):
        s.filter=Filter(arg)
        await asyncio.sleep (0.8)
    def __getattr__(s, *arg):
        return getattr(s.filter, *arg)

main_filter=effects("[in1] lowpass, [in2]amerge, asetrate=44100*1.2[out]")

async def deck1(x, index):
    std=aiofiles.stdout.buffer
    async for x,i in Deck(x):
        i=i[-1]
        await main_filter.ping_pong (i, index, std)

def just(i, x):
    assert(type(x)==int)
    assert(x>0)
    y=iter (i)
    while (x:=x-1)>=0:
        yield next(y)

async def filter_switch():
    i=0
    while True:
        [in1, in2]=[*map(lambda x: "in%d"%(x,), (2,1) if ((i:=i+1)%2)==0 else (1,2))]
        for j in range(100,300, 100):
            await main_filter.change(f"""[{in1}] lowpass,
                [{in2}]amerge, asetrate=44100*1.{j}[out]""")
        await main_filter.change(f"""[{in2}] anullsink;
            [{in1}]asetrate=44100*1.{j}[out]""")
        for j in range(100,300, -100):
            await main_filter.change(f"""[{in1}] lowpass,
                [{in2}]amerge, asetrate=44100*1.{j}[out]""")

        await main_filter.change(f"""[{in2}] anullsink;
            [{in1}]asetrate=44100*1.{j}[out]""")

async def main (cb, *args):
    await asyncio.gather(
        *map(lambda x: deck1(list(args), x), range(2)), filter_switch())


asyncio.run (main(*args()))
