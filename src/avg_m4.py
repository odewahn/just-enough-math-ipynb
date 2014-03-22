from collections import defaultdict
import sys

class Mapper (object):
    def __init__ (self):
        self.total = defaultdict(lambda: 0, {})
        self.count = defaultdict(lambda: 0, {})

    def map (self, key, val):
        self.total[key] += int(val)
        self.count[key] += 1

    def close (self):
        for key, val in self.total.items():
            print "%s\t%d\t%d" % ( key, val, self.count[key], )

m = Mapper()

for line in sys.stdin:
    key, val = line.strip().split("\t")
    m.map(key, val)

m.close()
