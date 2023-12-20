"""
Joel Bernstein
May 2022

Goal: turn a TF-Luna lidar sensor into a makeshift theremin instrument. The sensor will read
in distances in a constant stream which will be converted to frequencies in real time. These
will then be sent to the MIDI port to be played out loud.

Required: a TF-Luna sensor plugged into your serial port and an available MIDI port.
The control loop is built for the default Windows MIDI player. It will play a repeating
note at a given BPM until you move your hand far enough to play a new frequency.
"""

import serial
import mido
import time
import numpy as np

def readData(ser):
    
    while True:

        counter = ser.in_waiting
        if counter > 8:
            bytes_serial = ser.read(9)
            ser.reset_input_buffer()
            
            #If nothing wrong, this should be the value of the first 2 bytes
            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:
                distance = (bytes_serial[2] + bytes_serial[3]*256)/100. #Convert distance to m
                strength = bytes_serial[4] + bytes_serial[5]*256 #Signal strength out of 65535
                
                return distance, strength
            
#Ports. If midiPort is None, it will use the default midi Windows output
sensorPort = 'COM5'
midiPort = None

#Minimum, maximum, and tolerance (to keep same note) for distance
distLow = 0
distHigh = .3
distTol = .01

#This BPM decides how often a new note is sent when the pitch isn't changing.
bpm = 150.
noteDelay = 60./bpm

#Attempt to close serial port before opening
try:
    ser.close()
except:
    pass

#Open serial port
ser = serial.Serial(port=sensorPort,baudrate=115200,timeout=0)
if ser.isOpen() == False:
    ser.open()

#Attempt to close outport before opening
try:
    outport.close()
except:
    pass

#Open outport
if (midiPort==None):
    outport = mido.open_output()
else:
    outport = mido.open_output(midiPort)

#Define note pitch depending on distance bounds. Values can go from 0->127
distance, strength = readData(ser)
distOld = distance
noteOld = 0
while True:
    
    #Play at max velocity (attack) by default
    velocity = 127
    
    #Generate new note if meets requirements
    distance, strength = readData(ser)
    if (distance > distLow) and (distance < distHigh) and (np.abs(distance - distOld) > distTol):
        note = int((distance - distLow)/(distHigh - distLow)*127)
        
    #Play nothing if above max distance
    elif (distance > distHigh) or (distance < distLow):
        note = 0
        velocity = 0
        
    #Else, play old note
    else:
        #time.sleep(noteDelay)
        note = noteOld
        
    #Generate message
    msg = mido.Message('note_on',note=note,velocity=velocity)
    outport.send(msg)
    
    #Old distance and note
    distOld = distance
    noteOld = note