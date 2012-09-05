#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import cPickle as pickle
from collections import Counter

class SignalPredictor:
    
    def __init__(self, nLayer, db=None):
        assert nLayer > 0
        if db is None:
            self.__db = {}
        else:
            self.__db = db
        self.__history = [' ']
        self.__predicted = ' '
        self.__predictedLevel = 0
        self.__nLayer = nLayer

    def next(self, c):
        """
        Predict and learn.
        
        c :: str
           an input charactor.
        return :: p :: str, level :: int, success :: int
           predicted next charactor, 
           predicted level,
           and result of previous predicton (0 or 1).

        """
        assert isinstance(c, str)
        assert len(c) == 1

        #debug
        #print
        #print "input '%s'" % c

        # check
        if self.__predicted == c:
            success = 1
        else:
            success = 0
        
        # learn
        if success == 0:
            level = min(self.__predictedLevel + 1, self.__nLayer - 1)
            #print "learn %d '%s' '%s'" % (level, self.history(level + 1), c) #debug
            self.__db[self.history(level + 1)] = c

        # predict
        self.__history.append(c)
        if len(self.__history) > self.__nLayer:
            self.__history.pop(0)
            assert len(self.__history) == self.__nLayer
        p = c
        self.__predictedLevel = 0
        aL = range(0, self.__nLayer)
        aL.reverse()
        for level, history in map(lambda i : (i, self.history(i + 1)), aL):
            #print "level %d, history '%s'" % (level, history) #debug
            if history in self.__db:
                p = self.__db[history]
                #print "predict '%s' '%s'" % (history, p)
                self.__predictedLevel = level
                break
        #print "p '%s'" % p #debug
        self.__predicted = p

        # debug
        #print 'history', self.__history
        #print 'db', self.__db
        #print "input '%s' output '%s'" % (c, p)

        return p, level, success

    def history(self, length):
        """
        Get history by specified length.

        length :: int
        return :: str

        """
        assert isinstance(length, int)
        assert length <= self.__nLayer
        l = len(self.__history)
        return reduce(lambda s, c: s + c, self.__history[l - length:l], "")

    def dbSize(self):
        return len(self.__db)

    def nLayer(self):
        return self.__nLayer

    @classmethod
    def load(cls, reader):
        p = pickle.load(reader)
        assert isinstance(p, SignalPredictor)
        return p

    def dump(self, writer):
        pickle.dump(self, writer, protocol=-1)


class SignalPredictorWithCounter(SignalPredictor):

    def __init__(self, nLayer, db=None):
        self.count = Counter()
        SignalPredictor.__init__(self, nLayer, db=db)

    def step(self, c):
        _, _, success = self.next(c)
        self.count.update([success == 1])

    def size(self):
        return self.dbSize()

    def __str__(self):
        return "SignalPredictor(%d)" % self.nLayer()


def loopIterator(g):
    """
    g :: generator(str)
      input charactor generator.

    """
    history = []
    for c in g:
        history.append(c)
        yield c
    i = 0
    while True:
        yield history[i]
        i += 1
        if i == len(history):
            i = 0
            print '----------------------------------------------'

def forEachChar(f):
    """
    f :: file
       input file object.
    return :: generator(str)

    """
    while True:
        c = f.read(1)
        if not c:
            break
        if c.isalnum() or c == ' ' or c == '.':
            yield c

def consolidateSpaces(g):
    """
    g :: generator(str)
        input char generator.
    return :: generator(str)

    """
    isSpace = False
    for c in g:
        if c == ' ':
            isSpace = True
            continue
        else:
            if isSpace:
                yield ' '
                yield c
                isSpace = False
            else:
                yield c

class Rate:
    
    def __init__(self, size):
        """
        size :: int
          buffer size for moving average.

        """
        self.__size = size
        self.__history = []
        self.__nSuccess = 0

    def add(self, success):
        """
        success :: int
           1 for success, or 0.
        return :: float
            success rate.

        """
        assert isinstance(success, int)
        assert success == 1 or success == 0
        
        self.__nSuccess += success
        self.__history.append(success)
        if len(self.__history) > self.__size:
            self.__nSuccess -= self.__history.pop(0)
            assert len(self.__history) == self.__size
        
        return float(self.__nSuccess) / float(len(self.__history))


def doLearn(inputFile, nLayer, nChars, dumpFileName):
    assert isinstance(nLayer, int)
    assert isinstance(nChars, int)
    assert isinstance(dumpFileName, str)
    i = 0
    rate = Rate(10000)
    p = SignalPredictor(nLayer)
    for c in loopIterator(forEachChar(inputFile)):
        predicted, level, success = p.next(c)
        if predicted == ' ':
            predicted = '_'
        if c == ' ':
            c = '_'
        r = rate.add(success)
        
        print "%09d %s %s %2d %d %.6f %d" % (i, c, predicted, level, success, r, p.dbSize())
        i += 1
        if i >= nChars:
            break
    with open(dumpFileName, 'w') as f:
        p.dump(f)

def doPredict(inputFile, dumpFileName):
    assert isinstance(dumpFileName, str)
    with open(dumpFileName, 'r') as f:
        p = SignalPredictor.load(f)
    i = 0
    rate = Rate(10000)
    for c in consolidateSpaces(forEachChar(inputFile)):
        predicted, level, success = p.next(c)
        if predicted == ' ':
            predicted = '_'
        if c == ' ':
            c = '_'
        r = rate.add(success)
        
        print "%09d %s %s %2d %d %.6f %d" % (i, c, predicted, level, success, r, p.dbSize())
        i += 1

def main():
    errMsg = 'specify learn or predict as a command.\n' + \
        '  %s learn nLayer nChars dbFileName\n' % sys.argv[0] + \
        '  %s predict dbFileName' % sys.argv[0]
    if len(sys.argv) < 2:
        raise StandardError(errMsg)
    cmd = sys.argv[1]
    if cmd == 'learn':
        nLayer = int(sys.argv[2])
        nChars = int(sys.argv[3])
        dbFileName = sys.argv[4]
        doLearn(sys.stdin, nLayer, nChars, dbFileName)
    elif cmd == 'predict':
        dbFileName = sys.argv[2]
        doPredict(sys.stdin, dbFileName)
    else:
        raise ValueError(errMsg)

if __name__ == '__main__':
    main()
