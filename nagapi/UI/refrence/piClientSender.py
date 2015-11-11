'''
Created on 21 Sep 2015

@author: gregmeeresyoung
'''
import socket
import sys
import time
import Queue
import threading

from pixy import BlockArray,pixy_init,pixy_get_blocks

import ctypes
from ctypes import c_uint,Structure
import struct

class Blocks (Structure):
  _fields_ = [ ("type", c_uint),
               ("signature", c_uint),
               ("x", c_uint),
               ("y", c_uint),
               ("width", c_uint),
               ("height", c_uint),
               ("angle", c_uint) ]

class SeverCommad( object ):
    
    @staticmethod
    def wait(queue,connection):
        unpacker = struct.Struct('I')
        amount_expected = unpacker.size

        while True:
            # Look for the response
            amount_received = 0
            dataBuffer = ""
            while amount_received < amount_expected:
                
                dataBuffer = dataBuffer + connection.recv(amount_expected - amount_received)
                amount_received += len(dataBuffer)
                
                if amount_received == amount_expected:
                    unpacked_data = unpacker.unpack_from(dataBuffer, 0)
                    queue.put(unpacked_data[0])
                    # dont know if this is needed
                    queue.task_done()

###
# Initialize Pixy Interpreter thread #
pixy_init()
blocks = BlockArray(100)
frame = 0
##
# inisilise clasification
clasification = dict()
clasifiedTag = 0
maxPoints = 20
pointDataSize = 6

MOCAP_CLASSIFY_DATA = 2222
server_cmd = 1001

###
# Setup data stream
CMD_PASS = 1001
CMD_NEW_FRAME = 1002
CMD_ROGE_POINT = 6969

def buildPacker(numOfpoints,pointLength):
    frameData = ""
    pointData = "I"
    for i in xrange(1,pointLength):
        pointData  = pointData + " I"
         
    for i in xrange(0,numOfpoints):
        frameData = frameData +" "+ pointData

    return frameData

def buildFrameData(numOfpoints,pointDataSize):
    frameData = []
    for pindex in xrange(0,numOfpoints):
        for dindex in xrange(0,pointDataSize):
            frameData.append(9999)
    return frameData


sendPacker = struct.Struct(buildPacker(maxPoints,pointDataSize))
sendDataBuffer = ctypes.create_string_buffer(sendPacker.size)

frameData = buildFrameData(maxPoints,pointDataSize)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('HARD CODED TO MY PC NAME', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

##
# setup command queue thred
command_queue = Queue.Queue()
input_thread = threading.Thread(target=SeverCommad.wait, args=(command_queue,sock))
input_thread.daemon = True
input_thread.start()   

try:
    while True:
        frameData = buildFrameData(maxPoints,pointDataSize)
        numOfPointForFrame = pixy_get_blocks(100, blocks)
        frame = frame + 1
        if numOfPointForFrame > 0:
            numOfPointForFrame = numOfPointForFrame if numOfPointForFrame < maxPoints else maxPoints
            for index in xrange (0, numOfPointForFrame):
                # command to identify all point for frame have bee sent 
                cmd = CMD_PASS if index < ( numOfPointForFrame -1 ) else CMD_NEW_FRAME
                tag = index#blocks[index].signature
                colourID = blocks[index].signature
                x = blocks[index].x
                y = blocks[index].y
                w = blocks[index].width
                h = blocks[index].height
                
                dataIndexOffset = 0
                if tag != 0:
                    dataIndexOffset = tag * pointDataSize
                
                if tag != CMD_ROGE_POINT:
                    frameData[dataIndexOffset] = tag
                    frameData[dataIndexOffset+1] = colourID
                    frameData[dataIndexOffset+2] = x 
                    frameData[dataIndexOffset+3] = y 
                    frameData[dataIndexOffset+4] = w
                    frameData[dataIndexOffset+5] = h 
                
                if  cmd == CMD_NEW_FRAME:
                    break
                
        sendPacker.pack_into(sendDataBuffer, 0, *frameData) 
        sock.send(sendDataBuffer) 
        # new data is only reseve at 50 htz so wait a bit for new frame data to come of the camera
        time.sleep(.014)
        
        # check if we have a command form the server
        if not command_queue.empty():
            server_cmd = command_queue.get()
            print server_cmd,"got a server cmd"
            clasification = dict()
            clasifiedTag = 0
        


finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
    #recodingFile.close()
    
    