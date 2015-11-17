'''
Created on 5 Oct 2015

@author: gregmeeresyoung
'''
from PyQt4 import QtGui, QtCore
import sys
import yaml
import MocapClasify 
      
class MocapBox(QtGui.QGraphicsRectItem):


    def __init__(self,x,y,w,h):
        super(MocapBox, self).__init__(x,y,w,h)        
        self.color = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256,
                        QtCore.qrand() % 256)
        
        self.setBrush(self.color)
        self.mocapPointName = "unclasified"
        self.lable = QtGui.QGraphicsSimpleTextItem(self.mocapPointName,self)
        self.lable.rotate(180)
        self.lable.setPos(self.rect().x(),self.rect().y())
    
    def setRect(self, *args, **kwargs):
        self.lable.setPos(self.rect().x(),self.rect().y())
        return QtGui.QGraphicsRectItem.setRect(self, *args, **kwargs)
        
class ClasificationBox(QtGui.QGraphicsRectItem):

    green, red, blue = QtGui.QColor(0,255,0),QtGui.QColor(255,0,0),QtGui.QColor(0,0,255)
     
    def __init__(self,x,y,w,h):
        super(ClasificationBox, self).__init__(x,y,w,h)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        
        
        
        self.color = ClasificationBox.green #QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256,QtCore.qrand() % 256)
        
        self.setOpacity(.5)
        self.penWidth = 1.0
        
        self.setBrush(self.color)
        self._modifyed = False
        
        # data 
        self.clasifyData = dict(name='',
                                tag=0,
                                filter=dict(xChannel = dict(output=True,
                                                            noFilter=True,
                                                            lowPassFilter=False,
                                                            gasianAv=False,
                                                            freq=0.03,
                                                            filterbufferSize = 150),
                                            yChannel = dict(output=True,
                                                            noFilter=True,
                                                            lowPassFilter=False,
                                                            gasianAv=False,
                                                            freq=0.03,
                                                            filterbufferSize = 150                                                            ),
                                            wChannel = dict(output=False,
                                                            noFilter=True,
                                                            lowPassFilter=False,
                                                            gasianAv=False,
                                                            freq=0.03,
                                                            filterbufferSize = 150                                                            ),
                                            hChannel = dict(output=False,
                                                            noFilter=True,
                                                            lowPassFilter=False,
                                                            gasianAv=False,
                                                            freq=0.03,
                                                            filterbufferSize = 150                                                            ),
                                            ),
                    smartClasificaion =  dict(smartClasification=False,
                                              boxSize=40),
                    custemRege = dict(custemRegen=True,
                                      colourID=0,
                                      width=15,
                                      height=15,
                                      topLeftX=0,
                                      topLeftY=0,
                                      bottomRightX=0,
                                      bottomRightY=0),
                    output = dict(x=True,
                                  y=True,
                                  w=False,
                                  h=False))
    def setColour(self,colIndex):
        self.color = (ClasificationBox.green,ClasificationBox.red,ClasificationBox.blue)[colIndex -1]
        self.setBrush(self.color)
        
    def updatData(self):
        #print self.sceneBoundingRect().topLeft().x(),self.sceneBoundingRect().topLeft().y(),self.sceneBoundingRect().width(),self.sceneBoundingRect().height()
        self.clasifyData['custemRege']['width'] = self.sceneBoundingRect().width()
        self.clasifyData['custemRege']['height'] = self.sceneBoundingRect().height()
        self.clasifyData['custemRege']['topLeftX'] = self.sceneBoundingRect().topLeft().x()
        self.clasifyData['custemRege']['topLeftY'] = self.sceneBoundingRect().topLeft().y()
        self.clasifyData['custemRege']['bottomRightX'] = self.sceneBoundingRect().bottomRight().x() 
        self.clasifyData['custemRege']['bottomRightY'] = self.sceneBoundingRect().bottomRight().y()  
        self._modifyed = True

    def setData(self,data):
        
        self.clasifyData['name'] = str(data['name'])
        self.clasifyData['tag'] = data['tag']
        
        self.clasifyData['smartClasificaion']['smartClasification'] = data['smartClasificaion']['smartClasification']
        self.clasifyData['smartClasificaion']['boxSize'] = data['smartClasificaion']['boxSize']
        
        self.clasifyData['custemRege']['custemRegen'] = data['custemRege']['custemRegen']
        self.clasifyData['custemRege']['colourID'] = data['custemRege']['colourID']
        self.clasifyData['custemRege']['width'] = data['custemRege']['width']
        self.clasifyData['custemRege']['height'] = data['custemRege']['height']

        self.clasifyData['filter']['xChannel']['output'] = data['filter']['xChannel']['output']
        self.clasifyData['filter']['xChannel']['noFilter'] = data['filter']['xChannel']['noFilter']
        self.clasifyData['filter']['xChannel']['lowPassFilter'] = data['filter']['xChannel']['lowPassFilter'] 
        self.clasifyData['filter']['xChannel']['gasianAv'] = data['filter']['xChannel']['gasianAv']
        self.clasifyData['filter']['xChannel']['freq'] = data['filter']['xChannel']['freq']
        self.clasifyData['filter']['xChannel']['filterbufferSize'] = data['filter']['xChannel']['filterbufferSize']
        
        self.clasifyData['filter']['yChannel']['output'] = data['filter']['yChannel']['output']
        self.clasifyData['filter']['yChannel']['noFilter'] = data['filter']['yChannel']['noFilter']
        self.clasifyData['filter']['yChannel']['lowPassFilter'] = data['filter']['yChannel']['lowPassFilter'] 
        self.clasifyData['filter']['yChannel']['gasianAv'] = data['filter']['yChannel']['gasianAv']
        self.clasifyData['filter']['yChannel']['freq'] = data['filter']['yChannel']['freq']
        self.clasifyData['filter']['yChannel']['filterbufferSize'] = data['filter']['yChannel']['filterbufferSize']
        
        self.clasifyData['filter']['wChannel']['output']= data['filter']['wChannel']['output']
        self.clasifyData['filter']['wChannel']['noFilter'] = data['filter']['wChannel']['noFilter']
        self.clasifyData['filter']['wChannel']['lowPassFilter'] = data['filter']['wChannel']['lowPassFilter'] 
        self.clasifyData['filter']['wChannel']['gasianAv'] = data['filter']['wChannel']['gasianAv']
        self.clasifyData['filter']['wChannel']['freq'] = data['filter']['wChannel']['freq']
        self.clasifyData['filter']['wChannel']['filterbufferSize'] = data['filter']['wChannel']['filterbufferSize']
                
        self.clasifyData['filter']['hChannel']['output'] = data['filter']['hChannel']['output']
        self.clasifyData['filter']['hChannel']['noFilter'] = data['filter']['hChannel']['noFilter']
        self.clasifyData['filter']['hChannel']['lowPassFilter'] = data['filter']['hChannel']['lowPassFilter'] 
        self.clasifyData['filter']['hChannel']['gasianAv'] = data['filter']['hChannel']['gasianAv']
        self.clasifyData['filter']['hChannel']['freq'] = data['filter']['hChannel']['freq']
        self.clasifyData['filter']['hChannel']['filterbufferSize'] = data['filter']['hChannel']['filterbufferSize']
        self._modifyed = True   
    
    def getData(self):
        return self.clasifyData
    
    def getTag(self):
        return self.clasifyData['tag']
    '''
    def moveRect(self, move,offset):
        self.setPos( move -self.rect().center() )
    '''
    def modifyed(self):
        return self._modifyed
    
    def setModifyed(self,modifyed):
        self._modifyed = modifyed
                
class MocapScene(QtGui.QGraphicsScene):

    def __init__(self, parent=None):
        super(MocapScene, self).__init__(parent)
        self.setSceneRect(0, 0,640, 400 )
        self.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex) 
        
class MocapGraphicsView(QtGui.QGraphicsView):
    
    def __init__(self, parent):
        QtGui.QGraphicsView.__init__(self, parent)
        scene = MocapScene()
        
        self.setScene(scene)
        self.viewAngle = 180
        self.rotate(self.viewAngle)
        self._currentBox = None
        self.editRegen = False
        self.itemMovable = False
        #self.offset = QtCore.QPointF(0.0,0.0)   
    
    def updateSceneDataInCamraSpace(self):
        viewTransform = self.transform()
        #camera space
        viewTransform = viewTransform.rotate(-self.viewAngle)
        for item in self.scene().items():
            if type(item) == ClasificationBox:
                item.setTransform(viewTransform)         
                
        self._currentBox.updatData()
        self.emit(QtCore.SIGNAL("updateEditData()"))        
    
    def addMocapBox(self,mocapBox):
        self.scene().addItem(mocapBox)  
    
    def clear(self):
        for item in self.scene().items():
            if type(item) == ClasificationBox:
                item.setSelected(False)
                self.scene().removeItem(item)
        self._currentBox = None
        self.itemMovable = False   
        #self.offset = QtCore.QPointF(0.0,0.0)        
    
    def getClasificationRegens(self):
        data = dict()
        for item in self.scene().items():
            if type(item) == ClasificationBox:
                 
                itemData = item.getData()
                tagIndex = itemData['tag']
                coltag = itemData['custemRege']['colourID']
                tlx=itemData['custemRege']['topLeftX']
                tly=itemData['custemRege']['topLeftY'] 
                brx=itemData['custemRege']['bottomRightX']
                bry=itemData['custemRege']['bottomRightY'] 
                
                if data.has_key(coltag):
                    data[coltag].append(MocapClasify.Box(tlx,tly,brx,bry,tagIndex))
                else:
                    data[coltag] = [MocapClasify.Box(tlx,tly,brx,bry,tagIndex)]                                   
        return data 

    def buildFromData(self,clasifyData):
        w=clasifyData['custemRege']['width']
        h=clasifyData['custemRege']['height'] 
        x=clasifyData['custemRege']['topLeftX']
        y=clasifyData['custemRege']['topLeftY'] 
                        
        cBox = ClasificationBox(x,y,w,h)
        cBox.setColour(clasifyData['custemRege']['colourID']) 
        cBox.setData(clasifyData)
        self._currentBox = cBox
        
        self.scene().addItem(self._currentBox)
        self._currentBox.setSelected(False)
        self.itemMovable = False
        self.updateSceneDataInCamraSpace()

    def setModified(self,modified):
        for item in self.scene().items():
            if type(item) == ClasificationBox:
                item.setModifyed(modified)
    
    def isModified(self):
        for item in self.scene().items():
            if type(item) == ClasificationBox:
                return item.modifyed()
    
    def mousePressEvent(self, event):
        
        item = self.itemAt(event.pos())
        self._start = event.pos()
        
        for i in self.scene().selectedItems():
            i.setSelected(False)
        self._currentBox = None
        
        if self.editRegen:
            cBox = ClasificationBox(self._start.x(),self._start.y(),0,0)
            self._currentBox = cBox
            #self.offset = QtCore.QPointF(self.mapToScene(self._start))  - self._currentBox.rect().center()
            self.scene().addItem(self._currentBox)
            self._currentBox.setSelected(False)
            self.itemMovable = False
            self.updateSceneDataInCamraSpace()

        
        elif item and type(item) == ClasificationBox:
            item.setSelected(True)
            self.itemMovable = True
            #self.offset =   QtCore.QPointF(self.mapToScene(self._start))  - item.rect().center()
            self._currentBox = item
            self.updateSceneDataInCamraSpace()
            
        elif type(item) != ClasificationBox:
            self.itemMovable = False   
            #self.offset = QtCore.QPointF(0.0,0.0) 
        
        else:
            print type(item), len(self.scene().selectedItems())
        super(MocapGraphicsView, self).mousePressEvent(event)          

    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.
        """
        start = QtCore.QPointF(self.mapToScene(self._start))
        end = QtCore.QPointF(self.mapToScene(event.pos()))    
        
        w = abs((end.x() - start.x()))
        h = abs((end.y() - start.y())) 
        
        x = (start.x() + end.x())/2
        y = (start.y() + end.y())/2   
        
        lcx = x - (w/2)
        lcy = y - (h/2) 
        
        if self.editRegen:
            self._currentBox.setRect(lcx,lcy,w,h)
            self.updateSceneDataInCamraSpace()
           
        if self.itemMovable:
            self.updateSceneDataInCamraSpace()
        
        super(MocapGraphicsView, self).mouseMoveEvent(event)  
        
    def mouseReleaseEvent(self, event):
        
        start = QtCore.QPointF(self.mapToScene(self._start))
        end = QtCore.QPointF(self.mapToScene(event.pos()))    
        
        w = abs((end.x() - start.x()))
        h = abs((end.y() - start.y()))
        
        if self.editRegen and w < 10 and h < 10:
            QtGui.QMessageBox.warning(self, "Nagapi Mocap",
                    "regen to small")
            self.deletSelected()
                    
        self.editRegen = False
        self.emit(QtCore.SIGNAL("regenEditEnd()"))  
        super(MocapGraphicsView, self).mouseReleaseEvent(event)             
    
    def deletSelected(self):
        if self._currentBox:
            self._currentBox.setSelected(False)
            self.scene().removeItem(self._currentBox)
            self._currentBox = None
            self.itemMovable = False   
            #self.offset = QtCore.QPointF(0.0,0.0)
                        
    def regenSelected(self):
        return self._currentBox    

    def updateColour(self, colIndex):
        if self._currentBox:
            self._currentBox.setColour(colIndex)
    
    def resizeSelectedWidth(self,new_w):
        
        if self._currentBox:
            self._currentBox.setRect(self._currentBox.rect().topLeft().x(),
                                     self._currentBox.rect().topLeft().y(),
                                     new_w,
                                     self._currentBox.rect().height())
        
    def resizeSelectedHight(self,new_h):
        
        if self._currentBox:
            self._currentBox.setRect(self._currentBox.rect().topLeft().x(),
                                     self._currentBox.rect().topLeft().y(),
                                     self._currentBox.rect().width(),
                                     new_h)
    
    def getData(self):
        dump = dict()
        inc = 0
        for item in self.scene().items():
            if type(item) == ClasificationBox:
                dump[inc] = item.clasifyData
                inc= inc + 1        
        return dump
    
    def dumpData(self,stream):
        dump = dict()
        inc = 0
        for item in self.scene().items():
            if type(item) == ClasificationBox:
                dump[inc] = item.clasifyData
                inc= inc + 1
        yaml.dump(dump, stream)
        
        
        