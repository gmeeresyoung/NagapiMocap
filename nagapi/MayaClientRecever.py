'''
Created on 21 Sep 2015

@author: gregmeeresyoung
'''
import socket
import sys
import time
import ctypes
import struct

##
# Nagapi api imports 
from nagapi import FpsClock

###
# Setup data stream
CMD_PASS = 1001
CMD_NEW_FRAME = 1002
maxPoints = 20

def buildPacker(numOfpoints,pointData='I I I I I'):
    frameData = ""
    for i in xrange(0,numOfpoints):
        frameData = frameData +" "+ pointData

    return frameData

unpacker = struct.Struct(buildPacker(maxPoints))
amount_expected = unpacker.size

packer_cmd = struct.Struct('I')
cmdBuffer = ctypes.create_string_buffer(packer_cmd.size)
packer_cmd.pack_into(cmdBuffer, 0, CMD_NEW_FRAME) 
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('SQUID-HP', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
recordingFile = open('C:\\Users\\gregmeeresyoung\\workspace\\NagapifaceMocap\\fitering\\recordings\\clientRecording','w')
###
# Initalize fps clock
fpsclock = FpsClock(10)

try:
    while True:
        
        
        sock.send(cmdBuffer)
        # Look for the response
        amount_received = 0
        dataBuffer = ""
        
        while amount_received < amount_expected:
            dataBuffer = dataBuffer + sock.recv(amount_expected - amount_received)
            amount_received += len(dataBuffer)
            #print amount_received == amount_expected,amount_received,amount_expected
            if amount_received == amount_expected:
                
                unpacked_data = unpacker.unpack_from(dataBuffer, 0)
                recordingFile.write(str(unpacked_data)+"\n")
                '''
                for index in xrange(0,maxPoints):
                    dataIndexOffset = 0
                    if index != 0:
                        dataIndexOffset = index * 5 
                    cmd = unpacked_data[dataIndexOffset]
                    tag = unpacked_data[dataIndexOffset+1]
                    x = unpacked_data[dataIndexOffset+2] 
                    y = unpacked_data[dataIndexOffset+3] 
                    frame =unpacked_data[dataIndexOffset+4]  
                    #print cmd,tag,x,y,frame
                '''
        time.sleep(.02)
        fpsclock.printfps()
        

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
    recordingFile.close()