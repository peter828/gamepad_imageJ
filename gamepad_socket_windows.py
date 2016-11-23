import sys
from sys import path
import socket
from thread import *
import pygame
import os, json
import peyeFunctions as pf
import time

## AUTHOR: PETER PARK, peterpark828@gmail.com

# Initialize pygame
pygame.init()

# Initialize the joysticks
pygame.joystick.init()
jstick = pygame.joystick.Joystick(0) #assume only one joystick being connected.

print 'jstick', jstick


# Port connection
filename = 'port_index.txt'

with open(filename) as f: 
	index_str = f.read()

print "Connecting to PORT:" + index_str + "..."

PORT=int(index_str)

HOST = '' # Symbolic name meaning all available interfaces
#PORT = 2010 # Arbitrary non-previledged port


clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', PORT))
print "Gamepad socket is online."


## Main Program LOOP ##

done = False
jstick.init()

while (not done):
	for event in pygame.event.get(): # User did something
		
		if event.type == pygame.QUIT: # If user clicked close
			done = True

		
		#it seems the axis 3,4 send crazy amount of data so best to ignore them
		
	axes = jstick.get_numaxes()

	for i in range( axes ):
	#for i in axes:
		axis = round(jstick.get_axis(i),2)
		pf.cleanSend(clientsocket, ['axis', i, axis])
		receiverMessage = pf.cleanReceive(clientsocket)
		if receiverMessage == 'notok':
			eyeTraceAlive = False
			print 'eyeTrace does not want the gamepad data any more'
			break
			
			

	# Button
	pf.cleanSend(clientsocket, ['button', "a", jstick.get_button(0)])
	receiverMessage = pf.cleanReceive(clientsocket)

	pf.cleanSend(clientsocket, ['button', "b", jstick.get_button(1)])
	receiverMessage = pf.cleanReceive(clientsocket)

	pf.cleanSend(clientsocket, ['button', "x", jstick.get_button(2)])
	receiverMessage = pf.cleanReceive(clientsocket)

	pf.cleanSend(clientsocket, ['button', "y", jstick.get_button(3)])
	receiverMessage = pf.cleanReceive(clientsocket)

	pf.cleanSend(clientsocket, ['button', "l", jstick.get_button(4)])
	receiverMessage = pf.cleanReceive(clientsocket)

	pf.cleanSend(clientsocket, ['button', "r", jstick.get_button(5)])
	receiverMessage = pf.cleanReceive(clientsocket)

#print "gamepad data: " + reply
	if receiverMessage == 'notok':
		print 'Not ok from Fiji'
		break

	# limit to 60 frames per second 
	time.sleep(0.01)

clientsocket.close()
print 'Socket now closed'
