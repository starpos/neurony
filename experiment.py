# -*- coding: utf-8 -*-
"""
実験2
タイムマシンデータを1万文字ずつ順に食わせる
その過程でのメモリ消費量と正解率の変化を観察する
"""
import ngram
import brain
import spd
from collections import Counter
from time import clock

pds = map(lambda i: brain.Prediction.init_multi_leyer(i), xrange(1, 6))
spds = map(lambda i: spd.SignalPredictorWithCounter(i), xrange(1, 6))
ngs = map(lambda i: ngram.NGram(i), xrange(1, 6))

def iteration(tag, data):
    print "%d characters" % len(data)
    starttime = clock()
    for t in pds + spds + ngs:
        t.count = Counter()

    for c in data:
        for pd in pds:
            pd.count.update([pd.out_lower == c])
            pd.in_lower = c
            pd.step()

        for spd in spds:
            spd.step(c)

        for ng in ngs:
            ng.count.update([ng.expect() == c])
            ng.feed(c)

    N = float(len(data))
    for t in pds + spds + ngs:
        correct = 100 * t.count[True] / N
        size = t.size()
        print "%s: correct %.1f%% mem %d" % (
            t, correct, size)
        line = []
        line.append(tag)
        line.append(str(t))
        line.append(correct)
        line.append(size)
        buf.append(line)

    print clock() - starttime, "sec"
    print

timemachine = open("timemachine.txt")
buf = []
for i in range(20):
    nChars = 10000
    data = timemachine.read(nChars)
    iteration(str(nChars * i), data)

print "\n".join("\t".join(map(str, line)) for line in buf)
