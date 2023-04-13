import fobject

class Format(fobject.Format):
    def __init__(s, *a, **kw):
        s.args=a
        (fobject.Format).__init__(s, *a, *kw)
        pass
    def __repr__(s):
        return "AVFormat({0!r})".format(s.args)
    pass
def args():
    import sys
    yield from iter(sys.argv[1:])
    pass
x=[]
for i in args():
    j=Format(i)
    x.append(j)
    print(j)
    pass
print(x);
