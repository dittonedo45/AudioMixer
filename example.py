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
        print(a,file=sys.stderr)
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

def _get_str_filter (j):
    st=1
    def _swing(o):
        nonlocal st, j
        st=1 if st==2 else 2
        arg1=st
        arg2=1 if arg1==2 else 2

        return f"""[in{arg1}] lowpass, [in{arg2}]amerge,
    asetrate=44100*1.{j}, silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-90dB[out]"""
    return _swing
get_str_filter=_get_str_filter (1)

async def filter_switch():
    global main_filter
    global do_not_just_change
    i=0
    while True:
        await asyncio.sleep(19)
        if (i%2)==0:
            for j in range(100,300, 100):
                async with do_not_just_change:
                    main_filter=fobject.Filter (get_str_filter (j))
                await asyncio.sleep(0.8)
            main_filter=fobject.Filter(get_str_filter (j))
            await asyncio.sleep(80)
            for j in range(100,300, -100):
                async with do_not_just_change:
                    main_filter=fobject.Filter(get_str_filter (j))
                await asyncio.sleep(0.8)
            main_filter=fobject.Filter(get_str_filter (j))
        else:
            for j in range(100,300, 100):
                async with do_not_just_change:
                    main_filter=fobject.Filter(get_str_filter (j))
                await asyncio.sleep(0.8)
            main_filter=fobject.Filter(get_str_filter (j))
            await asyncio.sleep(80)
            for j in range(100,300, -100):
                async with do_not_just_change:
                    main_filter=fobject.Filter(get_str_filter (j))
                await asyncio.sleep(0.8)
            main_filter=fobject.Filter (get_str_filter (j))
        i=i+1

async def main (cb, *args):
    global do_not_just_change
    do_not_just_change=asyncio.Semaphore(2)
    await asyncio.gather(
        *map(lambda x: deck1(list(args),cb, x), range(2)),
        filter_switch()
        )

async def cbb(x, index):
    (self, frame)=x
    main_filter.send_frame_to_src(frame, index)

asyncio.run (main(cbb, *args()))
