import socket
import sys
'''
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 50000)
#print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

while True:
    #print >>sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(4096)
    print data
    print address
    
    #print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    #print >>sys.stderr, data
    
    if data:
        sent = sock.sendto(data, address)
        #print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
'''
BUFSIZE = 1024
port = 50000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
print 'udp echo server ready'
while 1:
	data, addr = s.recvfrom(BUFSIZE)
	print 'server received %r from %r' % (data, addr)
	s.sendto(data, addr)
