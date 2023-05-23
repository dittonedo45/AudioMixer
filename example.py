import fobject
import sys
import asyncio
import random
import aiofiles

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
    yield from iter(sys.argv[1:])
    pass

async def rand(l):
    loop=asyncio.get_running_loop()
    async def randint(*x):
        return await loop.run_in_executor (None, random.randint, *x)
    s=l[await randint(0,len(l)-1)]
    print(s)
    return s

async def Deck(tracks):
    while True:
        async def Format_(*x):
            return await run(Format, *x)
        x=await Format_(await rand(tracks))
        async for i in x:
            yield x, i
class Filter(fobject.Filter):
    pass
do_not_just_change=None
main_filter=Filter("[in1] lowpass, [in2]amerge, asetrate=44100*1.2[out]")

async def deck1(x, cb, index):
    global do_not_just_change
    std=aiofiles.stdout.buffer
    async for x, i in Deck(x):
        await cb(i, index)
        async with do_not_just_change:
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

async def filter_switch():
    global main_filter
    global do_not_just_change
    i=0
    while True:
        await asyncio.sleep(19)
        if (i%2)==0:
            for j in range(100,300, 100):
                async with do_not_just_change:
                    main_filter=fobject.Filter(f"""[in1] lowpass,
                        [in2]amerge, asetrate=44100*1.{j}[out]""")
                await asyncio.sleep(0.8)
            main_filter=fobject.Filter(f"""[in2] anullsink;
                [in1]asetrate=44100*1.{j}[out]""")
            await asyncio.sleep(80)
            for j in range(100,300, -100):
                async with do_not_just_change:
                    main_filter=fobject.Filter(f"""[in1] lowpass,
                        [in2]amerge, asetrate=44100*1.{j}[out]""")
                await asyncio.sleep(0.8)
            main_filter=fobject.Filter(f"""[in2] anullsink;
                [in1]asetrate=44100*1.{j}[out]""")
        else:
            for j in range(100,300, 100):
                async with do_not_just_change:
                    main_filter=fobject.Filter(f"""[in2] lowpass,
                        [in1]amerge, asetrate=44100*1.{j}[out]""")
                await asyncio.sleep(0.8)
            main_filter=fobject.Filter(f"""[in1] anullsink;
                [in2]asetrate=44100*1.{j}[out]""")
            await asyncio.sleep(80)
            for j in range(100,300, -100):
                async with do_not_just_change:
                    main_filter=fobject.Filter(f"""[in2] lowpass,
                        [in1]amerge, asetrate=44100*1.{j}[out]""")
                await asyncio.sleep(0.8)
            main_filter=fobject.Filter(f"""[in1] anullsink;
                [in2]asetrate=44100*1.{j}[out]""")
        i=i+1

async def main (cb, *args):
    global do_not_just_change
    do_not_just_change=asyncio.Semaphore(2)
    await asyncio.gather(*map(lambda x: deck1(list(args),
        cb, x), range(2)),
        filter_switch()
        )

async def cbb(x, index):
    (self, frame)=x
    main_filter.send_frame_to_src(frame, index)

asyncio.run (main(cbb, *args()))
