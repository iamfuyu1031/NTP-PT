import socket
import sys

# A simple udp echo server
BUFSIZE = 1024
port = 50000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
print 'udp echo server ready'
while 1:
	data, addr = s.recvfrom(BUFSIZE)
	print 'server received %r from %r' % (data, addr)
	s.sendto(data, addr)
