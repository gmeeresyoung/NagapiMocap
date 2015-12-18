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
        self.__sleepTime = 0.0
        
    def start(self):
        self.__fpsTimer_start = time.time()
    
    def speed(self):
        if self.__fpsTimer_start == None:
            self.__fpsTimer_start = time.time()
        
        timeForFrame = time.time() - self.__fpsTimer_start
        self.append(timeForFrame)
        try:
            ave = 1/float(average(self))
        except ZeroDivisionError:
            ave = 1000000
        
        self.__fpsTimer_start = timeForFrame + self.__fpsTimer_start          
        return ave
    
    def sleep(self):
        currentFps = self.speed()
        if currentFps > 50:
            self.__sleepTime = self.__sleepTime + .001
            time.sleep(self.__sleepTime )
        elif currentFps < 50 and self.__sleepTime:
            self.__sleepTime = self.__sleepTime - .001 
            time.sleep(self.__sleepTime )
        else:
            time.sleep(self.__sleepTime ) 
         
        
        
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
        
        