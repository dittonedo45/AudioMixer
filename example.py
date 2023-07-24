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
        s.percentage=0
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
    def calculate(self):
        d, m=self.duration (), self.max_duration ()
        self.percentage=100
        if d and m:
            self.percentage=(d/m)*100
        return self.percentage

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

class Deck(object):
    def __init__(s, tracks, cb, index):
        s.tracks=tracks
        s.cur_track=cb
        s.index=index
    async def __aiter__(s):
        while True:
            async def Format_(*x):
                return await run(Format, *x)
            try:
                x=await Format_(await rand(s.tracks))
                s.cur_track(x, s.index)
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
                res=file.flush ()
    async def ping_pong (main_filter, i, index, file):
        main_filter.send(i, index)
        frame=main_filter.get()
        await main_filter.write (frame, file)

class effects(object):
    def __init__(s, arg):
        s.filter=Filter(arg)
        s.stuff=[None, None]
    def add(s, arg, index):
        s.stuff[index]=arg
    async def change(s, arg, ch=False):
        if not ch:
            s.filter=Filter(arg)
        else:
            if not all(s.stuff):
                return
            [first,second]=[*map (lambda x: getattr(x, "calculate")(), s.stuff)]
            if (first<20):
                return
            if (second>60):
                return
            s.filter=Filter(arg)
        await asyncio.sleep (0.8)
    async def lip(self, time):
        await asyncio.sleep (time)
    async def ping_pong (s, *arg):
        if not all(s.stuff):
            return
        await s.filter.ping_pong(*arg)
    def __getattr__(s, *arg):
        return getattr(s.filter, *arg)

async def deck1(x, main_filter, index, file):
    async for x,i in Deck(x, main_filter.add, index):
        i=i[-1]
        await main_filter.ping_pong (i, index, file)

async def filter_switch(main_filter):
    i=0
    while True:
        [in1, in2]=[*map(lambda x: "in%d"%(x,), (2,1)
            if ((i:=i+1)%2)==0 else (1,2))]

        for j in range(100,300, 100):
            await main_filter.change(f"""[{in1}] lowpass,
                [{in2}]amerge, asetrate=44100*1.{j}[out]""", i!=1 or True)

        await main_filter.change(f"""[{in2}] anullsink;
            [{in1}]asetrate=44100*1.{j}[out]""", i!=1 or True)

        for j in range(100,300, -100):
            await main_filter.change(f"""[{in1}] lowpass,
                [{in2}]amerge, asetrate=44100*1.{j}[out]""", i!=1 or True)

        await main_filter.change(f"""[{in2}] anullsink;
            [{in1}]asetrate=44100*1.{j}[out]""", i!=1 or True)
        await main_filter.lip (19)

async def mixtape_handler (file,*args):
    main_filter=effects("[in1] lowpass, [in2]amerge, asetrate=44100*1.2[out]")
    await asyncio.gather(
        *map(lambda x: deck1(list(args), main_filter, x, file), range(2)),
        filter_switch(main_filter))

asyncio.run (mixtape_handler(sys.stdout.buffer, *args()))
