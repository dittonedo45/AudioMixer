import fobject
import sys, os
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
        s._stop=False
        s._max_d=s.max_duration()
        s._duration=0

    def duration_cb(s, arg):
        s._duration+=arg
    def len(s):
        return s.max_duration()

    def stop(s, arg=False):
        s._stop=arg
    def calculate(self):
        s=self
        if 0==s._max_d:
            s._max_d=s.len ()
        d, m=self.duration (), self._max_d
        if d and m:
            self.percentage=(d/m)*100
        else:
            self.percentage=100
        return self.percentage

    async def __aiter__(s):
        for i in s:
            if i==None:
                continue
            yield s, i
            await asyncio.sleep (0)
    def __repr__(s):
        return "AVFormat({0!r})".format(s.args[0])
    pass

def args():
    yield from iter(sys.argv[2:])
    pass

rand=random.Random(int(sys.argv[1],36)).choice
erand=random.Random(int(sys.argv[1],36)**2).choice

class Deck(object):
    def __init__(s, tracks, cb, index):
        s.tracks=tracks
        s.cur_track=cb
        s.index=index
        s._stop=False
    def stop(s, arg=False):
        s._stop=arg
    async def __aiter__(s):
        while True:
            try:
                x=Format(rand(s.tracks))
                s.cur_track(x, s.index)
            except SystemError as e:
                    continue
            else:
                lis=[*map(lambda x: os.path.join("effects", x),
                    os.listdir("effects"))]
                y=Format (ef:=erand(lis))
                async def tg(*s):
                    for i in s:
                        async for j in i:
                            yield j
                async for i in tg(x):
                    yield x, i

class Filter(fobject.Filter):
    def __init__(self, arg):
        fobject.Filter.__init__ (self, arg)
        self.dnc=asyncio.Semaphore(3)
    def get(self):
        return self.get_frame_from_sink ()
    def send(self, frame, index):
        self.send_frame_to_src(index, frame)
    def flush(self, index):
        self.send_frame_to_src(index)
    async def write (selffile):
        for pkt in res:
            file.write(pkt)
            file.flush ()
    async def ping_pong (main_filter, i, index, file):
        main_filter.send(i, index)
        await main_filter.write (file)

class effects(object):
    def __init__(s, arg):
        s.filter=Filter(arg)
        s.stuff=[None, None]
        s._stops=[None, None]
    def stop (s, arg):
        if arg==None:
            for i in filter(lambda x: not x is None, s._stops):
                i.stop (True)
            s._stops=[None, None]
        else:
            x=int(arg[2:])-1
            s._stops[x]=s.stuff[x]
            x=s._stops[x]
            if not x is None:
                x.stop ()
    def add(s, arg, index):
        s.stuff[index]=arg
    async def change(s, arg, ch=False):
        s.stop (None)
        if not ch:
            s.filter=Filter(arg)
        else:
            if not all(s.stuff):
                return
            [first,second]=[*map (lambda x: getattr(x, "calculate")(), s.stuff)]
            if (first<10):
                return
            if (second>80):
                return
            s.filter=Filter(arg)
        await asyncio.sleep (1.8)
    async def lip(self, time):
        await asyncio.sleep (time)
    async def ping_pong (s, *arg):
        if not all(s.stuff):
            return
        await s.filter.ping_pong(*arg)
    def __getattr__(s, *arg):
        return getattr(s.filter, *arg)

async def deck1(x, main_filter, index, file):
    lreserve=[]
    async for x,i in Deck(x, main_filter.add, index):
        i=i[-1]
        await main_filter.ping_pong (i, index, file)

async def filter_switch(main_filter):
    i=0
    while True:
        [in1, in2]=[*map(lambda x: "in%d"%(x,), (2,1)
            if ((i:=i+1)%2)==0 else (1,2))]

        for j in range(100,300, 100):
            await main_filter.change(f"""[{in1}]lowpass,
                [{in2}]amerge, asetrate=44100*1.{j}[out]""", i!=1 or True)

        await main_filter.change(f"""[{in2}] anullsink;
            [{in1}]asetrate=44100*1.{j}[out]""", i!=1 or True)
        main_filter.stop (in2)

        for j in range(100,300, -100):
            await main_filter.change(f"""[{in1}] lowpass,
                [{in2}]amerge, asetrate=44100*1.{j}[out]""", i!=1 or True)

        await main_filter.change(f"""[{in2}] anullsink;
            [{in1}]asetrate=44100*1.{j}[out]""", i!=1 or True)
        main_filter.stop (in2)
        await main_filter.lip (9)

async def mixtape_handler (file,*args):
    main_filter=effects("[in1] lowpass, [in2]amerge, asetrate=44100*1.2,aformat=channel_layouts=4.0[out]")
    await asyncio.gather(
        *map(lambda x: deck1(list(args), main_filter, x, file), range(2)),
        filter_switch(main_filter))

asyncio.run (mixtape_handler(sys.stdout.buffer, *args()))
