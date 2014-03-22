import sys

class Mapper (object):
    def map (self, key, val):
        print "%s\t%d" % ( key, int(val), )


m = Mapper()

for line in sys.stdin:
    key, val = line.strip().split("\t")
    m.map(key, val)
