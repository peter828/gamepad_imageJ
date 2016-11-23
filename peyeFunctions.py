#functions for the pure python scripts (outside imageJ)
import socket
import json
import struct
import numpy as np

def initSocket(port):
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind(('localhost', port))
	serversocket.listen(5)
	return serversocket
	
def cleanSend(socket, data):
	jsonData = json.dumps(data)
	socket.sendall(struct.pack('>i', len(jsonData)) + jsonData)
	
def cleanReceive(connection):
	packedSize = connection.recv(4)
	size = struct.unpack('>i', packedSize)[0]
	data = json.loads(connection.recv(size))
	return data
	
def avgDict(dict, medianFactor):
	x = np.zeros(len(dict))
	y = np.zeros(len(dict))
	for key in dict:
		xAvg = 0
		yAvg = 0
		count = 0
		for point in dict[key]:
			count = count + 1
			xAvg = xAvg + point[0]
			yAvg = yAvg + point[1]
		if count > 0:
			xAvg = xAvg/float(count)
			yAvg = yAvg/float(count)
		x[int(key)] = xAvg
		y[int(key)] = yAvg
	x = medfilt1(np.array(x),medianFactor)	
	y = medfilt1(np.array(y),medianFactor)	

	return x,y
	
def medfilt1(x=None,L=None):
    '''
    a simple median filter for 1d numpy arrays.

    performs a discrete one-dimensional median filter with window
    length L to input vector x. produces a vector the same size 
    as x. boundaries handled by shrinking L at edges; no data
    outside of x used in producing the median filtered output.
    (upon error or exception, returns None.)

    inputs:
        x, Python 1d list or tuple or Numpy array
        L, median filter window length
    output:
        xout, Numpy 1d array of median filtered result; same size as x
    
    bdj, 5-jun-2009
    '''
    # input checks and adjustments --------------------------------------------
    try:
        N = len(x)
        if N < 2:
            print 'Error: input sequence too short: length =',N
            return None
        elif L < 2:
            print 'Error: input filter window length too short: L =',L
            return None
        elif L > N:
            print 'Error: input filter window length too long: L = %d, len(x) = %d'%(L,N)
            return None
    except:
        print 'Exception: input data must be a sequence'
        return None
    xin = np.array(x)
    if xin.ndim != 1:
        print 'Error: input sequence has to be 1d: ndim =',xin.ndim
        return None 
    xout = np.zeros(xin.size)
    # ensure L is odd integer so median requires no interpolation
    L = int(L)
    if L%2 == 0: # if even, make odd
        L += 1 
    else: # already odd
        pass 
    Lwing = (L-1)/2
    # body --------------------------------------------------------------------
    for i,xi in enumerate(xin):
  
        # left boundary (Lwing terms)
        if i < Lwing:
            xout[i] = np.median(xin[0:i+Lwing+1]) # (0 to i+Lwing)
        # right boundary (Lwing terms)
        elif i >= N - Lwing:
            xout[i] = np.median(xin[i-Lwing:N]) # (i-Lwing to N-1)
        # middle (N - 2*Lwing terms; input vector and filter window overlap completely)
        else:
            xout[i] = np.median(xin[i-Lwing:i+Lwing+1]) # (i-Lwing to i+Lwing)
    return xout

def readTabDelimited(path):
	x = []
	y = []
	with open(path) as fp:
		for line in fp:
			x.append(int(line.split('\t')[0]))
			y.append(int(line.split('\t')[1]))
	return np.array([x,y])

def smoothData(a,smoothing):
	return np.array([medfilt1(a[0],smoothing) , medfilt1(a[1],smoothing)])