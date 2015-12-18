'''
Created on 7 Oct 2015

@author: gregmeeresyoung
'''
from MocapUtils import MOCAP_ROGE_DATA
from sklearn.neighbors import RadiusNeighborsClassifier
from sklearn import svm
from pprint import pprint
import numpy
import math


class Box(object):
    
    def __init__(self, topLeftx, topLefty,bottomRightx, bottemRighty,tag):
        bottemCornerPoint = (bottomRightx,bottemRighty)
        topCornerPoint = (topLeftx,topLefty)
        
        self._centroid = ( (((topLeftx - bottomRightx)/2) + bottomRightx),
                           (((topLefty - bottemRighty)/2) + bottemRighty))
        self._bc = bottemCornerPoint
        self._tc = topCornerPoint
        self._tag = tag
        
        self.tc = topCornerPoint
        self.bc = bottemCornerPoint
        
        self.__currentHits = []
        self._hitType = None
        
        self.__sortKeyFunc = lambda item : item[1]
    
    def updatBox(self,x,y,smartBox):
        topLeftPoint = (x-(smartBox),y-(smartBox))
        bottemRightPoint = (x+smartBox,y+smartBox)
        self._tc =  topLeftPoint
        self._bc = bottemRightPoint
        
        
        topLeftx,topLefty = topLeftPoint
        bottomRightx,bottemRighty = bottemRightPoint
        self._centroid = ( (((topLeftx - bottomRightx)/2) + bottomRightx),
                           (((topLefty - bottemRighty)/2) + bottemRighty))
        #self._centroid = ( x,y)
        
        # reset hits stored for frame
        self.clearHitPoints()
        # reset Hit type
        self._hitType = None
        
    def setHitType(self,hitType):
        self._hitType = hitType
    
    def addHitPoint(self,boxInfo,distange):
        # array ordered by distance
        self.__currentHits.append((boxInfo,distange))
        self.__currentHits = sorted(self.__currentHits, key=self.__sortKeyFunc )
    
    def clearHitPoints(self):
        self.__currentHits = []
        
    def getClosestPointBoxInfo(self):
        return self.__currentHits[0][0]

    def getClosestPointTag(self):
        return self.__currentHits[0][0][4].tag()
    
    def badPoint(self):
        if len(self.__currentHits) > 1:
            if self.__currentHits[0][1] == self.__currentHits[1][1]:
                return True
        return False
            
    
    def hitType(self):
        return self._hitType 
    
    def tag(self):
        return self._tag
    
    def centroid(self):
        return self._centroid
    
    def inBox(self,x,y):
        tpx,tpy = self._tc
        bpx,bpy = self._bc
        return x < bpx and x > tpx and y < bpy and y > tpy

class ClasifyMinDist( object ):
    
    goodPoint,badPoint,ambiguasPoint,notClasifyed = range(0,4)
    
    def __init__(self, data, maxNumOfPoints, smartBoxSize ):
        self._clasifyData = data
        self.__expectedPoints = self.getExpectedPoints()
        self._smartBoxSize = smartBoxSize
        self._updateBoxList = []
        
        self.__clasifyedPointsForFrame = {}
        self.__missingPoints = []
        self.__extraPoints = []
        
    def resetForNestFrame(self):
        self.__clasifyedPointsForFrame = {}
        self.__missingPoints = []
        self.__extraPoints = []
        self._updateBoxList = []
        
    def getExpectedPoints(self):
        expectedPoints = {}
        for coltag in self._clasifyData.keys():
            for box in self._clasifyData[coltag]:        
                expectedPoints[box.tag()] = box
                
        return expectedPoints        
    
    def pointsProcessedForFrame(self,tag,box):
        self.__clasifyedPointsForFrame[tag]
    
    def distold(self,x,y):   
        return numpy.sqrt(numpy.sum((x-y)**2))    
    
    def dist(self,p1,p2):
        x = numpy.array(p1)
        y = numpy.array(p2)          
        return numpy.sqrt(numpy.sum((x-y)**2))  
    
    def numpy_calc_dist(self,p1,p2):
        return numpy.linalg.norm(numpy.array(p1)-numpy.array(p2))

    def math_calc_dist(self,p1,p2):
        return math.sqrt(math.pow((p2[0] - p1[0]), 2) +
                         math.pow((p2[1] - p1[1]), 2))

    def regenClasify(self,tagIn,coltag,x,y):

        ##
        #I have fliped the data to work with the UI portrat layout. this need to be controled by the ui 
        #
        screenspace_x,screenspace_y = x*2,y*2
        smallestDistance  = 1000000
        boxinfo  = (None,None,None,None,None)
        tag = None
        
        if self._clasifyData.has_key(coltag):
            for box in self._clasifyData[coltag]:
                
                a = box.centroid()#p1
                b = (screenspace_x,screenspace_y)#p2
                distance = self.math_calc_dist(a,b)#self.dist(a,b)
                if distance < self._smartBoxSize:
                    if distance <= smallestDistance:
                        smallestDistance = distance
                        tag = box.tag()
                        boxinfo = (box.updatBox,
                                         screenspace_x,
                                         screenspace_y,
                                         self._smartBoxSize,
                                         box)
        
        if tag != None: 
            box = boxinfo[4]

            if box.hitType() == self.goodPoint:
                box.setHitType(self.ambiguasPoint)
                tag = MOCAP_ROGE_DATA     
            else:
                box.setHitType(self.goodPoint)        

            self._updateBoxList.append(boxinfo) 
            return tag
        else:
            return MOCAP_ROGE_DATA    
    
    def updateBoxesForNextFrame(self):
        for func,arg1,arg2,arg3,box in self._updateBoxList:
            if box.hitType() == self.ambiguasPoint:
                pass

            else:
                func(arg1,arg2,arg3)
        
        self.resetForNestFrame()
            
class ClasifyMinDistEXPERIMENTAL( object ):
    
    goodPoint,badPoint,ambiguasPoint,notClasifyed = range(0,4)
    
    def __init__(self, data, maxNumOfPoints, smartBoxSize ):
        self._clasifyData = data
        self.__expectedPoints = self.getExpectedPoints()
        self._smartBoxSize = smartBoxSize
        self._updateBoxList = {}
        
        self.__clasifyedPointsForFrame = {}
        self.__missingPoints = []
        self.__extraPoints = []
        
    def resetForNestFrame(self):
        self.__clasifyedPointsForFrame = {}
        self.__missingPoints = []
        self.__extraPoints = []
        #self._updateBoxList = {}
        
    def getExpectedPoints(self):
        expectedPoints = {}
        for coltag in self._clasifyData.keys():
            for box in self._clasifyData[coltag]:        
                expectedPoints[box.tag()] = box
                
        return expectedPoints        
    
    def pointsProcessedForFrame(self,tag,box):
        self.__clasifyedPointsForFrame[tag]
    
    def distold(self,x,y):   
        return numpy.sqrt(numpy.sum((x-y)**2))    
    
    def dist(self,p1,p2):
        x = numpy.array(p1)
        y = numpy.array(p2)          
        return numpy.sqrt(numpy.sum((x-y)**2))  
    
    def numpy_calc_dist(self,p1,p2):
        return numpy.linalg.norm(numpy.array(p1)-numpy.array(p2))

    def math_calc_dist(self,p1,p2):
        return math.sqrt(math.pow((p2[0] - p1[0]), 2) +
                         math.pow((p2[1] - p1[1]), 2))

    def regenClasify(self,tag,coltag,x,y,w,h,dataIndexOffset):

        ##
        #I have fliped the data to work with the UI portrat layout. this need to be controled by the ui 
        #
        screenspace_x,screenspace_y = x*2,y*2
        smallestDistance  = 1000000
        boxinfo  = (None,None,None,None,None)
        tag = None
        
        if self._clasifyData.has_key(coltag):
            for box in self._clasifyData[coltag]:
                
                a = box.centroid()#p1
                b = (screenspace_x,screenspace_y)#p2
                distance = self.math_calc_dist(a,b)#self.dist(a,b)

                if distance <= smallestDistance:
                    smallestDistance = distance
                    tag = box.tag()
                    boxinfo = (box.updatBox,
                                     screenspace_x,
                                     screenspace_y,
                                     self._smartBoxSize,
                                     box,(coltag,tag, x, y, w, h,dataIndexOffset) )
        
        if tag != None: 
            box = boxinfo[4]
            # box has been hit
            box.addHitPoint(boxinfo,smallestDistance)
            # test for two points with zero distance 
            if box.badPoint():
                print "norty point",box.tag()
                tag = MOCAP_ROGE_DATA
            else:
                # we have good point 
                boxinfo = box.getClosestPointBoxInfo()
                tag = box.getClosestPointTag()
            '''   
            if boxinfo[4].hitType() == self.goodPoint:
                boxinfo[4].setHitType(self.ambiguasPoint)
                tag = MOCAP_ROGE_DATA     
            else:
                boxinfo[4].setHitType(self.goodPoint)        
            ''' 
            self._updateBoxList[tag] = boxinfo

            return tag
        else:
            return MOCAP_ROGE_DATA    
    
    def updateForNextFrame(self):
        return self._updateBoxList.values()
    
    def updateBoxesForNextFrame(self):
        for func,arg1,arg2,arg3,box,data in self._updateBoxList.values():
            if box.badPoint():
                box.clearHitPoints()
            else:
                func(arg1,arg2,arg3)
        
        self.resetForNestFrame()

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
                    
                    if box.hitType() == self.goodPoint:
                        print "ambigues point",box.tag()
                        box.setHitType(self.ambiguasPoint)
                    else:
                        box.setHitType(self.goodPoint)
                        
                    self._updateBoxList.append( (box.updatBox,
                                                 screenspace_x,
                                                 screenspace_y,
                                                 self._smartBoxSize,
                                                 box))
                    #print "clasifye",box.tag()
                    return box.tag()
        
        #print "lost clasification" 
        return MOCAP_ROGE_DATA#btag      
    
    def updateBoxesForNextFrame(self):
        
        for func,arg1,arg2,arg3,arg4 in self._updateBoxList:
            #if arg4.hitType() == self.ambiguasPoint:
                #print "abigues point",arg4.tag()
            func(arg1,arg2,arg3)
        
        self._updateBoxList = []


class ClasifyRadiusNeighbors( object ):
    
    goodPoint,badPoint,ambiguasPoint,notClasifyed = range(0,4)
    
    def __init__(self, data, maxNumOfPoints, smartBoxSize ):
        self._clasifyData = self.build(data,smartBoxSize)
        self._smartBoxSize = smartBoxSize        
        
    def build(self,data,smartBoxSize):
        newDataFormat = dict()
        for clotag,boxes in data.items():
            centroids = []
            labels = []
            tagPointDict = dict()
            for box in boxes:
                centroidx,centroidy = box.centroid()
                centroids.append([centroidx,centroidy])
                labels.append(box.tag())
                tagPointDict[box.tag()] = [centroidx,centroidy] 
            newDataFormat[clotag] = dict(neigh=RadiusNeighborsClassifier(radius=smartBoxSize),
                                         data=tagPointDict)
            newDataFormat[clotag]['neigh'].fit(centroids,labels)
        return newDataFormat
        
    def regenClasify(self,tag,coltag,x,y):
        screenspace_x,screenspace_y = x*2,y*2
        
        if self._clasifyData.has_key(coltag):            
            try:
                tag = self._clasifyData[coltag]['neigh'].predict([[screenspace_x,screenspace_y]])
                tag = tag[0]
                self._clasifyData[coltag]['data'][tag] = [screenspace_x,screenspace_y]       
                
            except ValueError:
                return MOCAP_ROGE_DATA   
            return tag
        return MOCAP_ROGE_DATA
    
    def updateBoxesForNextFrame(self):
        for clotag,data in self._clasifyData.items():
            centroids = []
            labels = []
            for tag,centroid in data['data'].items():
                centroids.append(centroid)
                labels.append(tag)
            self._clasifyData[clotag]['neigh'].fit(centroids,labels)            
        
        
             
X = [[229.5, 500.5], [127.0, 497.0]]#[[0,0], [1,1], [2,2], [3,3]]
y = [1, 5]#[5, 1, 3, 4]
neigh = RadiusNeighborsClassifier(radius=1.0)
neigh.fit(X, y) 
print(neigh.predict([[229.5, 500.5]]))



