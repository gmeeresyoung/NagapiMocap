'''
Created on 22 Sep 2015

@author: gregmeeresyoung
'''
from collections import deque
from numpy import average
import time
import sys

class FpsClock(deque):
    '''
    classdocs
    '''


    def __init__(self, size):
        '''
        Constructor
        '''
        super(FpsClock, self).__init__(maxlen=size)
        self.__fpsTimer_start = None
    
    def start(self):
        self.__fpsTimer_start = time.time()
    
    
    def fps(self):
        if self.__fpsTimer_start == None:
            self.__fpsTimer_start = time.time()
        timeForFrame = time.time() - self.__fpsTimer_start
        self.append(timeForFrame)
        try:
            ave = int(1/average(self))

        except OverflowError:
            ave = 100000
        
        sys.stdout.write(" FPS[ %d ] "%(ave))
        sys.stdout.flush()
        self.__fpsTimer_start = timeForFrame + self.__fpsTimer_start
        
    def printfps(self):
        
        if self.__fpsTimer_start == None:
            self.__fpsTimer_start = time.time()
        
        timeForFrame = time.time() - self.__fpsTimer_start
        self.append(timeForFrame)
        try:
            ave = int(1/average(self))
        except OverflowError:
            ave = 1000000
        
        print (" FPS[ %d ] "%(ave))
        self.__fpsTimer_start = timeForFrame + self.__fpsTimer_start    
        
        