from threading import Thread
#from Queue import *
import Queue
import time
import socket
import random,string


# Generate a random string to send
def randomword(length):
	return ''.join(random.choice(string.lowercase+string.digits) for i in range(length))

# Send thread
def send_data(s):
 	global finished
	#global send_q
	while not finished:
		data = randomword(random.randint(10,100))
		s.send(data)
		print 'Sending-------------------------------------'
		print data
		#send_q.put(data)
		time.sleep(10)

# Receive thread
def recv_data(s, size):
 	global finished
	#global recv_q
	while not finished:
		data = s.recv(size)
		print 'Receiving-------------------------------------'
		print data
		#recv_q.put(data)
		


if __name__ == '__main__':
	host = 'localhost' 
	port = 10000 
	size = 1024 
	finished = False
	#send_q = Queue.Queue()
	#recv_q = Queue.Queue()
	# Set up a socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))
	# Start the send thread
	TIMQ = Thread(target = send_data, args = (s,))
	TIMQ.daemon = True
	TIMQ.start()
	# Start the recv thread
	TIMQ = Thread(target = recv_data, args = (s,size,))
	TIMQ.daemon = True
	TIMQ.start()
	# Stop the threads
	raw_input("Press Enter to stop...")
	finished = True
	print '#'*30
	#while send_q.get():
	#print send_q.get()
	#print recv_q.get()
