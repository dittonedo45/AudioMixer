import fobject
from fobject import show_all_bytes
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

packates=Pac()

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
            yield s, s.send_frame(i)
            try:
                while True:
                    yield s, s.send_frame(None)
                    await asyncio.sleep(0)
            except EOFError: pass
            else: continue

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
    global packates
    while True:
        async def Format_(*x):
            return await run(Format, *x)

        try:
            x=await Format_(await rand(tracks))
        except SystemError as e:
                continue
        else:
            async for i in x:
                packates.append(*i[1:])
                yield x, i
class Filter(fobject.Filter):
    async def parse_and_config (*arg):
        fobject.Filter.parse_and_config(*arg)

async def deck1(main_filter, x, index):
    std=aiofiles.stdout.buffer
    async for x, i in Deck(x):
        main_filter.send_frame_to_src(i[1], index)
        frame=main_filter.get_frame_from_sink()
        if not (isinstance(frame, (int))):
            for pkt in main_filter.swallow (frame):
                std.write(pkt)


def just(i, x):
    assert(type(x)==int)
    assert(x>0)
    y=iter (i)
    while (x:=x-1)>=0:
        yield next(y)

async def filter_switch(main_filter):
    i=0
    while True:
        #await asyncio.sleep(19)
        if (i%2)==0:
            for j in range(100,300, 100):
                await main_filter.parse_and_config(f"""[in1] lowpass,
                        [in2]amerge, asetrate=44100*1.{j}[out]""")
                await asyncio.sleep(0.8)
            await main_filter.parse_and_config(f"""[in2] anullsink;
                [in1]asetrate=44100*1.{j}[out]""")
            await asyncio.sleep(1)
            for j in range(100,300, -100):
                await main_filter.parse_and_config(f"""[in1] lowpass,
                        [in2]amerge, asetrate=44100*1.{j}[out]""")
                await asyncio.sleep(0.8)
            await main_filter.parse_and_config(f"""[in2] anullsink;
                [in1]asetrate=44100*1.{j}[out]""")
        else:
            for j in range(100,300, 100):
                await main_filter.parse_and_config(f"""[in2] lowpass,
                        [in1]amerge, asetrate=44100*1.{j}[out]""")
                await asyncio.sleep(0.8)
            await main_filter.parse_and_config(f"""[in1] anullsink;
                [in2]asetrate=44100*1.{j}[out]""")
            await asyncio.sleep(1)
            for j in range(100,300, -100):
                await main_filter.parse_and_config(f"""[in2] lowpass,
                        [in1]amerge, asetrate=44100*1.{j}[out]""")
                await asyncio.sleep(0.8)
            await main_filter.parse_and_config(f"""[in1] anullsink;
                [in2]asetrate=44100*1.{j}[out]""")
        i=i+1
async def go_do_something():
    while True:
        for i in packates[:-10]:
                await asyncio.sleep (10.0)
        await asyncio.sleep (0.01)

async def main (*args):
    main_filter=Filter("[in1] lowpass, [in2]amerge, asetrate=44100*1.2[out]")
    await main_filter.parse_and_config ("[in1] lowpass, [in2]amerge, asetrate=44100*1.2[out]")
    await asyncio.gather(
        *map(lambda x: deck1(main_filter, list(args), x), range(2)),
        go_do_something(),
        filter_switch(main_filter)
        )


asyncio.run (main(*args()))
