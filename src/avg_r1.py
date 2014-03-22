import sys

class Reducer (object):
    def reduce (self, key, values):
        self.total = 0
        self.count = 0

        for val in values:
            self.total += int(val)
            self.count += 1

        avg = self.total / float(self.count)
        print "%s\t%f" % ( key, avg, )

last_key = None

for line in sys.stdin:
    key, val = line.strip().split("\t")

    if not last_key == key:
        if last_key:
            r.reduce(last_key, values)

        r = Reducer()
        values = []

    values.append(val)
    last_key = key

r.reduce(key, values)
