'''
Created on 7 Oct 2015

@author: gregmeeresyoung
'''
from scipy.ndimage import filters
from scipy.interpolate import UnivariateSpline
from collections import deque
from scipy.signal import gaussian,butter,lfilter

class CircularBuffer(deque):
    def __init__(self, size=0,lowPassFreq = .15):
        super(CircularBuffer, self).__init__(maxlen=size)
        self._b = gaussian(39, 10)
        self._lb, self._la = butter(4, lowPassFreq, 'lowpass', analog=False)

    def updateFilterFrequecy(self,lowPassFreq):
        self._lb, self._la = butter(4, lowPassFreq, 'lowpass', analog=False)
    
    def filterGauss(self):
        return filters.convolve1d(self, self._b/self._b.sum())[-1]
    
    def filterButterworth(self):
        fl = lfilter(self._lb,self._la, self)[-1]
        return long(fl)
    

if __name__ == '__main__':
    pass