'''
Created on 7 Oct 2015

@author: gregmeeresyoung
'''
import sys,os,re
import socket
import select
import Queue
from collections import deque
import ctypes
import struct
from pprint import pprint
from PyQt4.QtCore import QThread,SIGNAL
from PyQt4.QtGui import QMessageBox

from MocapFilters import CircularBuffer
from MocapUtils import *
import MocapClasify

from nagapi import FpsClock
###
# Initalize fps clock
fpsclock = FpsClock(10)


class Server(QThread):

    nofilter,lowPassFilter,gouseanFilter = range(0,3)
    
    def __init__(self, parent = None):
    
        QThread.__init__(self, parent)
        self.exiting = False
        self.commandFromServer=None
        # Give the connection a queue for data we want to send/ reseve
        self.data_queues = dict()
        self.receve_queues = dict()
        self.pluginCommand = dict()
        
        # set up data streem for commands 
        self.packer_cmd = struct.Struct('I')
        self.cmdBuffer = ctypes.create_string_buffer(self.packer_cmd.size)
        self.amount_expected_cmd = self.packer_cmd.size
        # setup data streem for mocp data
        self.filterBufferSize = 100
        self.maxPoints = 20
        self.pointDataSize = 6        
        self.packer_data = struct.Struct(self.buildPacker(self.maxPoints,self.pointDataSize))
        self.sendDataBuffer = ctypes.create_string_buffer(self.packer_data.size)
        self.amount_expected_mocap = self.packer_data.size
        
        self._clasfyRegens = None
        self.setClasifydata = False
        
        self.smartFilterBoxSize = 40
        self.filterDataFlag = False
        self.frameDataBuffer = self.buildFrameData(self.maxPoints,self.pointDataSize) 
        
        self.filterBuffers = {rbID:dict(x=dict(buffer=CircularBuffer(size=self.filterBufferSize),
                                            filterType=Server.lowPassFilter,
                                            lowPassFreq = .003),
                                        y=dict(buffer=CircularBuffer(size=self.filterBufferSize),
                                             filterType=Server.lowPassFilter,
                                             lowPassFreq = .003),
                                        w=dict(buffer=CircularBuffer(size=self.filterBufferSize),
                                             filterType=Server.lowPassFilter,
                                             lowPassFreq = .003),
                                        h=dict(buffer=CircularBuffer(size=self.filterBufferSize),
                                             filterType=Server.lowPassFilter,
                                             lowPassFreq = .003),
                                        activeChannels=dict(x=True,
                                                          y=True,
                                                          w=False,
                                                          h=False)) for rbID in xrange(0,self.maxPoints)}
    # file recording
        finc = 0
        fileName = "mocapRecording" 
        self.recordToFile = False
        self.openRecording = False
        for f in os.listdir("./"):
            if re.search(fileName, f):
                finc = finc + 1
        self.rocodingFileName = '%s%d.txt'%(fileName,finc)
        
    def buildFromData(self,data):
        
        tag = data['tag']
        channel = 'x'
        self.updateOutputChannel(tag,channel, data['filter']['%sChannel'%channel]['output'] )
        newSize = data['filter']['%sChannel'%channel]['filterbufferSize']
        self.updateBufferSize(tag,channel,newSize)

        newFreq = data['filter']['%sChannel'%channel]['freq']
        self.updateLowPassFreq(tag,channel,newFreq)
        
        if data['filter']['%sChannel'%channel]['noFilter']:
            filterType = Server.nofilter
        elif data['filter']['%sChannel'%channel]['lowPassFilter']:
            filterType = Server.lowPassFilter
        else:
            filterType = Server.nofilter
        self.updateFilterType(tag,channel,filterType)
        
        channel = 'y'
        self.updateOutputChannel(tag,channel, data['filter']['%sChannel'%channel]['output'] )
        newSize = data['filter']['%sChannel'%channel]['filterbufferSize']
        self.updateBufferSize(tag,channel,newSize)

        newFreq = data['filter']['%sChannel'%channel]['freq']
        self.updateLowPassFreq(tag,channel,newFreq)
        
        if data['filter']['%sChannel'%channel]['noFilter']:
            filterType = Server.nofilter
        elif data['filter']['%sChannel'%channel]['lowPassFilter']:
            filterType = Server.lowPassFilter
        else:
            filterType = Server.nofilter
        self.updateFilterType(tag,channel,filterType)
        
        channel = 'w'
        self.updateOutputChannel(tag,channel, data['filter']['%sChannel'%channel]['output'] )
        newSize = data['filter']['%sChannel'%channel]['filterbufferSize']
        self.updateBufferSize(tag,channel,newSize)

        newFreq = data['filter']['%sChannel'%channel]['freq']
        self.updateLowPassFreq(tag,channel,newFreq)
        
        if data['filter']['%sChannel'%channel]['noFilter']:
            filterType = Server.nofilter
        elif data['filter']['%sChannel'%channel]['lowPassFilter']:
            filterType = Server.lowPassFilter
        else:
            filterType = Server.nofilter
        self.updateFilterType(tag,channel,filterType)
        
        channel = 'h'
        self.updateOutputChannel(tag,channel, data['filter']['%sChannel'%channel]['output'] )
        newSize = data['filter']['%sChannel'%channel]['filterbufferSize']
        self.updateBufferSize(tag,channel,newSize)

        newFreq = data['filter']['%sChannel'%channel]['freq']
        self.updateLowPassFreq(tag,channel,newFreq)
        
        if data['filter']['xChannel']['noFilter']:
            filterType = Server.nofilter
        elif data['filter']['xChannel']['lowPassFilter']:
            filterType = Server.lowPassFilter
        else:
            filterType = Server.nofilter
        self.updateFilterType(tag,channel,filterType)
        
        smartBoxSize = data['smartClasificaion']['boxSize']
        self.updateSmartBox(smartBoxSize)
    
    def buildPacker(self,numOfpoints,pointLength):
        frameData = ""
        pointData = "I"#'I I I I I'
        for i in xrange(1,pointLength):
            pointData  = pointData + " I"
             
        for i in xrange(0,numOfpoints):
            frameData = frameData +" "+ pointData
    
        return frameData
    
    def buildFrameData(self,numOfpoints,pointDataSize):
        frameData = []
        for pindex in xrange(0,numOfpoints):
            for dindex in xrange(0,pointDataSize):
                frameData.append(MOCAP_ROGE_DATA)
        return frameData
    
    def __del__(self):
        print "deleating thred"
        self.exiting = True
        self.tcpServer.close()
        self.wait()       
         
    def render(self,lisenPort,mocapclientIP,pluginClientIP):
        print lisenPort,mocapclientIP,pluginClientIP
        self.exiting = False
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.setblocking(0)    
            
        # Bind the socket to the port
        server_address = ('', lisenPort)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        self.tcpServer.bind(server_address)
        
        # Listen for incoming connections
        self.tcpServer.listen(2)        

        # wait for a connection for give time then close in none found
        self.timeout = 60
        
        # Sockets from which we expect to read
        self.inputs = [ self.tcpServer ]
        self.mocapSendClientIP = [ mocapclientIP ]
        
        
        # Sockets to which we expect to write
        self.outputs = [ ]

        if pluginClientIP:
            self.readCliantIP = [ pluginClientIP ]
        else:
            self.readCliantIP = [  ]

        self.start()
        
    def closeServer(self):
        self.exiting = True
        self.tcpServer.close()
            
    def updateSmartBox(self, smartBoxSize):
        self.smartFilterBoxSize = smartBoxSize
    
    def updateBufferSize(self,tag,channel,newSize):
        print tag,channel,newSize,self.filterBuffers[tag][channel]['buffer'] 
        self.filterBuffers[tag][channel]['buffer'] = CircularBuffer(size=newSize)
    
    def updateFilterType(self,tag,channel,filterType):
        print tag,channel,filterType,self.filterBuffers[tag][channel]['filterType'] 
        self.filterBuffers[tag][channel]['filterType'] = filterType


    def updateLowPassFreq(self,tag,channel,newFreq):
        print tag,channel,newFreq,self.filterBuffers[tag][channel]['lowPassFreq']
        self.filterBuffers[tag][channel]['lowPassFreq'] = newFreq

    
    def updateOutputChannel(self,tag,channel,on):
        print tag,channel,on,self.filterBuffers[tag]['activeChannels'][channel] 
        self.filterBuffers[tag]['activeChannels'][channel] = on
       
       
    def clasifyData(self,data):
        print "clasifyData"
        self.commandFromServer = MOCAP_CLASSIFY_DATA
        self._clasfyRegens = MocapClasify.Clasify(data,self.maxPoints,self.smartFilterBoxSize)
        self.setClasifydata = True
        self.filterDataFlag = False 
           
    def rawData(self):
        print "raw data"
        self.commandFromServer = MOCAP_RAW_DATA
        # not point filtering unclasifyed data
        self.setClasifydata = False
        self.filterDataFlag = False
    
    def filterData(self):
        print "filter data"
        #data needs to be clasifyed to filter
        self.commandFromServer = MOCAP_CLASSIFY_DATA
        self.setClasifydata = True
        self.filterDataFlag = True
    
    def filterOff(self):
        self.filterDataFlag = False        
        
    def startRecording(self,curRecordFile):
        self.openRecording = open(curRecordFile, "w")
    
    def stopRecording(self):
        if self.openRecording:
            self.openRecording.close()
            self.openRecording = None
       
    def run(self):
        while not self.exiting and self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, self.timeout)    
            if not (readable or writable or exceptional) or self.exiting:
                # setting readable to [] is a hack to get the server to close down without an error 
                readable = []
                self.exiting = True
            
            # Handle inputs
            for s in readable:        
                if s is self.tcpServer:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    print >>sys.stderr, 'new connection from', client_address
                    connection.setblocking(0)                
                    # sort cnections for imputs and output servers
                    if client_address[0] in self.readCliantIP:
                        
                        # only alow one plugin connection at the mo
                        # if already output remove befor adding new one
                        #append new imput connection 
                        self.outputs.append(connection)
                        # ring buffer might be slow
                        self.data_queues[connection] = deque(maxlen =500)#Queue.Queue(maxsize=1000)#LifoQueue
                        self.pluginCommand[connection] = None
                        self.receve_queues[connection] = (Queue.Queue(),self.packer_cmd,self.amount_expected_cmd)
                        self.inputs.append(connection)
                        
                    if client_address[0] in self.mocapSendClientIP: 
                        self.inputs.append(connection)
                        self.outputs.append(connection)
                        self.pluginCommand[connection] = None
                        self.receve_queues[connection] = (Queue.Queue(),self.packer_data,self.amount_expected_mocap)
                        
                    else:
                        raise "dont know this server",client_address
                else: 
                    # Look for the response
                    queue,packer,amount_expected  = self.receve_queues[s]
                    try:
                        amount_received,dataBuffer = queue.get_nowait()
                    except Queue.Empty:
                        amount_received,dataBuffer = (0,"")# get from mesage que
                                
                    dataBuffer = dataBuffer + s.recv(amount_expected - amount_received)            
                    amount_received = len(dataBuffer)
                                
                    if amount_expected == amount_received:
        
                        unpacked_data = packer.unpack_from(dataBuffer, 0)
                        
                        ##
                        # get commad form plugin client
                        #
                        if amount_expected == self.amount_expected_cmd: 
                            for key in self.data_queues.keys():
                                self.pluginCommand[s] = unpacked_data[0]
                        ##
                        # get data from mocap client 
                        #                              
                        elif   amount_expected == self.amount_expected_mocap:
                            
                            '''
                            if self.openRecording:
                                self.openRecording.write(str(unpacked_data) + "\n")
                            '''
                            ##
                            # look for user input commands 
                            #
                            if self.commandFromServer:
                                self.pluginCommand[s] = self.commandFromServer
                                # reset servercommand
                                self.commandFromServer = None
                            
                            for index in xrange(0,self.maxPoints):
                                dataIndexOffset = 0
                                if index != 0:
                                    dataIndexOffset = index * self.pointDataSize

                                tag = unpacked_data[dataIndexOffset]
                                coltag = unpacked_data[dataIndexOffset+1]
                                ##
                                #I have fliped the data this need to be controled by the ui 
                                #
                                y = unpacked_data[dataIndexOffset+2]
                                x = unpacked_data[dataIndexOffset+3] 
                                h = unpacked_data[dataIndexOffset+4] 
                                w = unpacked_data[dataIndexOffset+5] 

                                if self.setClasifydata:
                                    # setup nural pos tages done once to enable consistant traking
                                    # of named points , once done smart clasification is used
                                    #self._clasfyRegens.assingTags(tag,coltag,x,y,w,h)
                                    tag = self._clasfyRegens.regenClasify(tag,coltag,x,y)
                                
                                if tag != MOCAP_ROGE_DATA:
                                    if self.filterDataFlag:
                                        
                                        if self.filterBuffers[tag]['activeChannels']['x']:
                                            
                                            self.filterBuffers[tag]['x']['buffer'].append(x)
                                            
                                            if self.filterBuffers[tag]['x']['filterType'] ==  Server.lowPassFilter:
                                                x = self.filterBuffers[tag]['x']['buffer'].filterButterworth()  
                                            elif self.filterBuffers[tag]['x']['filterType'] ==  Server.gouseanFilter:
                                                x = self.filterBuffers[tag]['x']['buffer'].filterGauss() 
                                            else:
                                                # no filter
                                                pass

                                        if self.filterBuffers[tag]['activeChannels']['y']:
                                            self.filterBuffers[tag]['y']['buffer'].append(y)
                                            if self.filterBuffers[tag]['y']['filterType'] ==  Server.lowPassFilter:
                                                y = self.filterBuffers[tag]['y']['buffer'].filterButterworth()  
                                            elif self.filterBuffers[tag]['y']['filterType'] ==  Server.gouseanFilter:
                                                y = self.filterBuffers[tag]['y']['buffer'].filterGauss() 
                                            else:
                                                # no filter
                                                pass
                                            
                                        if self.filterBuffers[tag]['activeChannels']['w']:
                                            self.filterBuffers[tag]['w']['buffer'].append(w)
                                            if self.filterBuffers[tag]['w']['filterType'] ==  Server.lowPassFilter:
                                                w = self.filterBuffers[tag]['w']['buffer'].filterButterworth()  
                                            
                                            elif self.filterBuffers[tag]['w']['filterType'] ==  Server.gouseanFilter:
                                                w = self.filterBuffers[tag]['w']['buffer'].filterGauss()                                        
                                            else:
                                                # no filter
                                                pass
                                            
                                        if self.filterBuffers[tag]['activeChannels']['h']:
                                            self.filterBuffers[tag]['h']['buffer'].append(h)
                                            if self.filterBuffers[tag]['h']['filterType'] ==  Server.lowPassFilter:
                                                h = self.filterBuffers[tag]['h']['buffer'].filterButterworth()  
                                            elif self.filterBuffers[tag]['h']['filterType'] ==  Server.gouseanFilter:
                                                h = self.filterBuffers[tag]['h']['buffer'].filterGauss()                                             
                                            else:
                                                # no filter
                                                pass
                                        #x = self.filterBuffers[tag]['bx'].filterButterworth()       
                                        #y = self.filterBuffers[tag]['by'].filterButterworth() 
                                    
                                    self.emit(SIGNAL("subFrame(int, long, long, long, long)"),
                                              tag, x, y,w,h)                                       
                                    
                                self.frameDataBuffer[dataIndexOffset] = tag
                                self.frameDataBuffer[dataIndexOffset+1] = coltag
                                self.frameDataBuffer[dataIndexOffset+2] = x
                                self.frameDataBuffer[dataIndexOffset+3] = y
                                self.frameDataBuffer[dataIndexOffset+4] = w
                                self.frameDataBuffer[dataIndexOffset+5] = h
                                    

                            if self.setClasifydata:
                                self._clasfyRegens.updateBoxesForNextFrame()
                            
                            '''       
                            if self.filterDataFlag:
                                unpacked_data = self.frameDataBuffer
                            '''
                            
                            self.emit(SIGNAL("frameEnd()"))                            
                            
                            packer.pack_into(self.sendDataBuffer, 0, *self.frameDataBuffer)
                            
                            if self.openRecording:
                                self.openRecording.write(str(self.frameDataBuffer) + "\n")
                                
                            # put data in que for all cliant servers reding mocap data
                            for key in self.data_queues.keys():
                                self.data_queues[key].append(self.sendDataBuffer)                                        
    
                    else:
                        # set for next pass
                        queue.put((amount_received,dataBuffer))
    
            # Handle outputs
            for s in writable:
    
                if self.pluginCommand[s] == CMD_NEW_FRAME:
                    try:
            
                        next_msg = self.data_queues[s].pop()
                        
                    except IndexError:
                        # No messages waiting so stop checking for writability.
                        print >>sys.stderr, 'output queue for', s.getpeername(), 'is empty'
                    else:
                        s.send(next_msg)
                        self.pluginCommand[s] =  None
            
                elif  self.pluginCommand[s] == MOCAP_CLASSIFY_DATA:
                    pass

                    print "sending clasify comand to mocap cliant"
                    '''
                    self.packer_cmd.pack_into(self.cmdBuffer, 0, MOCAP_CLASSIFY_DATA) 
                    s.send(self.cmdBuffer)
                    '''
                    self.pluginCommand[s] = None

                
                elif self.pluginCommand[s] == MOCAP_RAW_DATA:
                    print "sending raw data comand to cliant"
                    self.packer_cmd.pack_into(self.cmdBuffer, 0, MOCAP_RAW_DATA) 
                    s.send(self.cmdBuffer)
                    self.pluginCommand[s] = None
                else:
                    # no commands to exicutep
                    self.pluginCommand[s] = None            
            
            # Handle "exceptional conditions"
            for s in exceptional:
                print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
                # Stop listening for input on the connection
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                # close recoding to file
                #recordingFile.close()
                # Remove message queue
                del self.data_queues[s]
                del self.receve_queues[s]
        
        
        self.tcpServer.close()                
        self.exit()
        self.emit(SIGNAL("stopingServer()"))
        
        
        
if __name__ == '__main__':
    pass