'''
Created on 7 Oct 2015

@author: gregmeeresyoung
'''
from MocapUtils import MOCAP_ROGE_DATA


class Box(object):
    
    def __init__(self, topLeftx, topLefty,bottomRightx, bottemRighty,tag):
        bottemCornerPoint = (bottomRightx,bottemRighty)
        topCornerPoint = (topLeftx,topLefty)
        self._bc = bottemCornerPoint
        self._tc = topCornerPoint
        self._tag = tag
        
        self.tc = topCornerPoint
        self.bc = bottemCornerPoint
    
    def updatBox(self,x,y,smartBox):
        topLeftPoint = (x-(smartBox),y-(smartBox))
        bottemRightPoint = (x+smartBox,y+smartBox)
        self._tc =  topLeftPoint
        self._bc = bottemRightPoint
        
    def tag(self):
        return self._tag
    
    def inBox(self,x,y):
        tpx,tpy = self._tc
        bpx,bpy = self._bc
        return x < bpx and x > tpx and y < bpy and y > tpy
    

class Clasify( object ):
    
    goodPoint,badPoint,ambiguasPoint,notClasifyed = range(0,4)
    
    def __init__(self, data, maxNumOfPoints, smartBoxSize ):
        self._clasifyData = data
        self._smartBoxSize = smartBoxSize
        self._updateBoxList = []

    def regenClasify(self,tag,coltag,x,y):
        screenspace_x,screenspace_y = x*2,y*2
        
        if self._clasifyData.has_key(coltag):
            for box in self._clasifyData[coltag]:
                if box.inBox(screenspace_x,screenspace_y):
                    self._updateBoxList.append( (box.updatBox,
                                                 screenspace_x,
                                                 screenspace_y,
                                                 self._smartBoxSize))
                    #print "clasifye",box.tag()
                    return box.tag()
        
        #print "lost clasification" 
        return MOCAP_ROGE_DATA#btag      
    
    def updateBoxesForNextFrame(self):
        for func,arg1,arg2,arg3 in self._updateBoxList:
            func(arg1,arg2,arg3)
        self._updateBoxList = []
        
