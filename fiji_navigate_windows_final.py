from bdv import BigDataViewer
from bdv.export import ProgressWriterConsole
from net.imglib2.realtransform import AffineTransform3D
from bdv.viewer import DisplayMode
import time
import socket
from thread import *
from ast import literal_eval as make_tuple
import operator 
import threading
import time 
import struct 
import json
import ij
from ij import IJ
import math
from random import randint

# this script receives inputs from the gamepad and lets the user navigate through. 

## AUTHOR: PETER PARK, peterpark828@gmail.com

# move2D() takes axis value and direction from the controller to move in 2D.
def move2D(axisval, dir):
	transform = AffineTransform3D()
	# get the current transform
	v.getState().getViewerTransform(transform)

	# global transform
	# get the canvas and its size
	canvas = v.getDisplay()
	width = canvas.getWidth()
	height = canvas.getHeight()
	
	#calculate the center of the view (in data coordinates)
	dx = 0
	dy = 0
	
	# horizontal 
	if dir == 'h':
		dx = axisval

	# vertical 
	if dir == 'v':
		dy = axisval


	transform.set(
		transform.get(0,0), 0, 0, transform.get(0,3)-increment*dx,
		0, transform.get(1,1), 0, transform.get(1,3)-increment*dy,
		0, 0, 				   1, 			    transform.get(2,3))
	
	v.setCurrentViewerTransform( transform );


	
# swim3D() takes button "A" and 'B" to move through depth
def swim3D(butval, factorSwim):
	transform = AffineTransform3D()
	# get the current transform
	v.getState().getViewerTransform(transform)

	dz = butval * factorSwim 

	transform.set(
		transform.get(0,0), 0, 0, transform.get(0,3),
		0, transform.get(1,1), 0, transform.get(1,3),
		0, 0, 				   1, transform.get(2,3)-dz)
	v.setCurrentViewerTransform( transform );
		

# scopeMove() takes button "Y" and "X" to make the scope larger or smaller
def scopeMove(button, zoomFactor):
	transform = AffineTransform3D()
	# get the current transform
	v.getState().getViewerTransform(transform)
	
	# get the canvas and its size
	canvas = v.getDisplay()
	width = canvas.getWidth()
	height = canvas.getHeight()
	
	#calculate the center of the view (in data coordinates)
	centerX = (transform.get(0,3) - width/2 ) /float(transform.get(0,0))
	centerY = (transform.get(1,3) - height/2) /float(transform.get(1,1))
	centerZ = transform.get(2,3)

	# zoom in
	if button == "y":
		n = 1 + zoomFactor/float(100)
	# zoom out
	elif button == "x":
		n = 1 - zoomFactor/float(100)
	
	# scale the transform
	transform.scale( n ) 
	transform.set(
			transform.get(0,0), 0,    0,      centerX * float(transform.get(0,0)) + width/2,
			0, transform.get(1,1),    0,      centerY * float(transform.get(1,1)) + height/2,
			0,                  0, 	  1, 	  centerZ);
	
	
	# apply the transfrom
	v.setCurrentViewerTransform( transform )
	
# rotate3D() takes R1 and L1 to rotate in 3D (NOT USED IN THIS VERSION) 
def rotate3D(button, turnFactor, axis):
	transform = AffineTransform3D()
	# get the current transform
	v.getState().getViewerTransform(transform)
	
	# get the canvas and its size
	canvas = v.getDisplay()
	width = canvas.getWidth()
	height = canvas.getHeight()

	# how much you turn
	n = turnFactor*float(math.pi/180)*1/2 #turnFactor is in degrees; needs to be converted to radian
										  #also halved to reduce speed
	
	# rotate the other way around
	if button == "l":
		n = float(2*math.pi) - n 
	
	# scale the transform
	transform.rotate(axis,n) 
	
	# apply the transfrom
	v.setCurrentViewerTransform( transform )

	
def scopeMoveChair(axisval, zoomFactor): #NOT USED IN THIS VERSION
	transform = AffineTransform3D()
	# get the current transform
	v.getState().getViewerTransform(transform)
	
	# get the canvas and its size
	canvas = v.getDisplay()
	width = canvas.getWidth()
	height = canvas.getHeight()
	
	#calculate the center of the view (in data coordinates)
	centerX = (transform.get(0,3) - width/2 ) /float(transform.get(0,0))
	centerY = (transform.get(1,3) - height/2) /float(transform.get(1,1))
	centerZ = transform.get(2,3)

	# zoom in/out
	n = 1 + axisval*zoomFactor/float(100)

	
	# scale the transform
	transform.scale( n ) 
	transform.set(
			transform.get(0,0), 0,    0,      centerX * float(transform.get(0,0)) + width/2,
			0, transform.get(1,1),    0,      centerY * float(transform.get(1,1)) + height/2,
			0,                  0, 	  1, 	  centerZ);
	
	
	# apply the transfrom
	v.setCurrentViewerTransform( transform )

def cleanSend(socket, data):
	jsonData = json.dumps(data)
	socket.sendall(struct.pack('>i', len(jsonData)) + jsonData)

	
def cleanReceive(connection):
	packedSize = connection.recv(4)
	size = struct.unpack('>i', packedSize)[0]
	data = json.loads(connection.recv(size))
	return data


def fetchData(connection):
	output = cleanReceive(connection)
	cleanSend(connection, 'ok')
	return output


class threadUpdate(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket


	def run (self):
		# global msg_str
		
		global xJoy
		global yJoy
		global rJoy
		global buttonA
		global buttonB
		global buttonX
		global buttonY
		global buttonL
		global buttonR
		global legangle
		global pitch
		

		
		padSocket = self.socket
		connection, address = padSocket.accept()

		while 1:
			msg = fetchData(connection)			
			if str(msg[0]) == 'axis':
				if int(msg[1]) == 0:
					xJoy = msg[2]
				elif int(msg[1]) == 1:
					yJoy = msg[2]
				elif int(msg[1]) == 2:
					rJoy = msg[2]
				

			elif str(msg[0]) == 'button':
				if msg[1] == 'a':
					buttonA = msg[2]
				if msg[1] == 'b':
					buttonB = msg[2]
				if msg[1] == 'x':
					buttonX = msg[2]
				if msg[1] == 'y':
					buttonY = msg[2]
				if msg[1] == 'l':
					buttonL = msg[2]
				if msg[1] == 'r':
					buttonR = msg[2]

			time.sleep(0.01)


#Implements the threading for multiple types of input devices


class threadInput (threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID


	def run (self):

		global xJoy
		global yJoy
		global rJoy
		global buttonA
		global buttonB
		global buttonX
		global buttonY
		global buttonL
		global buttonR
		global legangle
		global pitch

		if self.threadID == "gamepad":
			print "Gamepad thread initiated"

			done = False 

			while (not done):
				
				# parsing the type of input 

				# horizontal
				if abs(xJoy) > joyThreshold:
					move2D(xJoy, "h")

				# vertical 
				if abs(yJoy) > joyThreshold:
					move2D(yJoy, "v")

				if abs(rJoy) > turnJoyThreshold:
					if rJoy < 0:
						swim3D(-1, 0.1)
					elif rJoy > 0:
						swim3D(1, 0.1)
						
				if int(buttonA) == 1:
					swim3D(1, 0.7)

				if int(buttonB) == 1 :
					swim3D(-1, 0.7)

				if int(buttonX) == 1:
					scopeMove("x",5)

				if int(buttonY) == 1:
					scopeMove("y",5)

				if int(buttonR) == 1:
					scopeMove("y",1)
				
				if int(buttonL)== 1:
					scopeMove("x",1)


				time.sleep(0.01)

			done = false				

		### Put more function for other input devices 

		else:
			print "ERROR: Invalid thread type"
	


#################### Script Start #####################
try: 
	## Server Socket 
	# creates a server socket

	# create an AF_INET, STREAM socket (TCP)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print 'Socket Created'

	# set timeout: 30 seconds
	s.settimeout(30)

	# Connect to the localhost
	PORT = randint(1111,9999)
	file = open("INSERT YOUR PATH",'w')
	file.write(str(PORT))
	file.close()
	print "Socket Index: "+ str(PORT) 

	s.bind(('localhost', PORT))
	s.listen(10)
	print "Socket now listening"
						
	xJoy, yJoy, rJoy, buttonA, buttonB, buttonX, buttonY, buttonL, buttonR, legangle, pitch = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

	path="INSERT YOUR PATH"
	## Navigation using Big Data Viewer 
	bdv = BigDataViewer(path, 'BDV Title', ProgressWriterConsole())
	v = bdv.getViewer()
	v.setDisplayMode( DisplayMode.FUSED);
	bdv.getViewerFrame().setVisible( True );

	# initialize transform 
	transform = AffineTransform3D()
	increment = 10
	#zoomFactor = 5 # in percent
	joyThreshold = 0.2
	turnJoyThreshold = 0.2
	


	# create update thread
	updateTh = threadUpdate(s)
	updateTh.start()
	# create gamepad thread
	gamepadTh = threadInput("gamepad")
	gamepadTh.start()

	updateTh.join()
	gamepadTh.join()




except Exception, e:
	print 'Exception global'
	print e

except socket.error, msg:
	print 'Failed to create socket. Error code: '+ str(msg[0]) +' , Error message : '+ msg[1]
	sys.exit()
