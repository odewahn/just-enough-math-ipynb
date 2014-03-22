import sys

class Reducer (object):
    def reduce (self, key, values):
        self.total = 0
        self.count = 0

        for _total, _count in values:
            self.total += int(_total)
            self.count += int(_count)

        avg = self.total / float(self.count)
        print "%s\t%f" % ( key, avg, )


last_key = None

for line in sys.stdin:
    vals = line.strip().split("\t")
    key = vals.pop(0)

    if not last_key == key:
        if last_key:
            r.reduce(last_key, values)

        r = Reducer()
        values = []

    values.append(vals)
    last_key = key

r.reduce(key, values)
