#!/usr/bin/python
# The code is modified from a simple tcp port forwarder http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/
# We modified it to transform tcp into udp packets. The target udp packet will follow NTP protocol exactly.
import socket
import select
import time
import sys
import decode_ntp_no_fte
import encode_as_ntp_no_fte
import aes
import binascii
import multiprocessing
import random
import Queue
import xml.etree.ElementTree as ET


def port_forwarding(host, port):
	forward = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		forward.connect((host, port))
		return forward
	except Exception, e:
		print e
		return False


def server_init(conn_host, conn_port):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((conn_host, conn_port))
	server.listen(200)
	return server

def server_recv_data(conn_host, conn_port, fwd_host, fwd_port, data, server, timing, start, a,b,c,d):
#def server_recv_data(conn_host, conn_port, fwd_host, fwd_port, data, server):
	#server = server_init(conn_host, conn_port)
	input_list = []
	channel = {}
	addr = {}

	input_list.append(server)
	while 1:
		time.sleep(delay)
		ss = select.select
		inputready, outputready, exceptready = ss(input_list, [], [])
		for s in inputready:
			if s == server:
				server_on_accept(server, input_list, channel, fwd_host, fwd_port, addr)
				break
			data = s.recv(buffer_size)
			if len(data) == 0:
				server_on_close(s, input_list, channel)
				break
			else:
				# If there is data, check timing
				#shared_data.put(data)
				send_p = multiprocessing.Process(target = send_one_packet, args = (s, data, channel, timing, start, addr, fwd_host, fwd_port, a,b,c,d,))
				send_p.start()
				send_p.join()
				#data_incoming_remaining, aes_encryption_remaining, aes_decryption_remaining, data_outgoing_remaining = server_on_recv(s, data, channel, addr, fwd_host, fwd_port, data_incoming_remaining, aes_encryption_remaining, aes_decryption_remaining, data_outgoing_remaining)

def server_on_accept(server, input_list, channel, fwd_host, fwd_port, addr):
	forward = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#forward = port_forwarding(fwd_host, fwd_port)
	clientsock, clientaddr = server.accept()
	if forward:
		print clientaddr, "has connected"
		input_list.append(clientsock)
		input_list.append(forward)
		channel[clientsock] = forward
		channel[forward] = clientsock
		addr[clientsock] = (fwd_host, fwd_port)
		addr[forward] = clientaddr
	else:
		print "Can't establish connection with remote server."
		print "Closing connection with client side", clientaddr
		clientsock.close()

def server_on_close(s, input_list, channel):
	print s.getpeername(), "has disconnected"
	#remove objects from input_list
	input_list.remove(s)
	input_list.remove(channel[s])
	out = channel[s]
	# close the connection with client
	channel[out].close()  # equivalent to do self.s.close()
	# close the connection with remote server
	channel[s].close()
	# delete both objects from channel dict
	del channel[out]
	del channel[s]

def server_on_recv(s, data, channel, addr, fwd_host, fwd_port, a,b,c,d):
	aes_encryption_remaining = a.get()
	aes_decryption_remaining = b.get()
	data_incoming_remaining = c.get()
	data_outgoing_remaining = d.get()
	#print data
	#channel[s].send(data)
	# here we can parse and/or modify the data before send forward
	if addr[s] == (fwd_host, fwd_port):
		# Use a string of length 5 to represent the length of data
		data = str(len(data)).zfill(5) + data
		all_data, data_incoming_remaining = encode_as_ntp_no_fte.handle_data(data, 63, data_incoming_remaining)
		print 'udp'
		if all_data != []:
			#print 'yes'
			for j in range(len(all_data)):
				# Transform the packet into NTP
				#output = encode_as_ntp.transform_string(data)
				# AES encryption and convert into hex
				aes_output = aes.aes_encrypt(all_data[j], key, padding, block_size).encode('hex')
				# Combine the data with the AES remaining from last connection
				#aes_output += self.aes_encryption_remaining
				aes_encryption_remaining =  aes_encryption_remaining + aes_output
				# Map AES result into NTP
				output, aes_encryption_remaining = encode_as_ntp_no_fte.transform_aes_into_ntp(aes_encryption_remaining)
				for i in range(0, len(output)):
					channel[s].sendto(output[i].decode('hex'), addr[s])
	else:
		print 'tcp'
		#self.channel[self.s].send('hello world')
		# When there is an NTP packet coming, decode it
		#print 'there is data'
		#print data
		output2 = decode_ntp_no_fte.recover_ntp_into_aes(data.encode('hex'))
		aes_decryption_remaining += output2
		if len(aes_decryption_remaining) >= 176:
			tmp = aes_decryption_remaining[:176]
			aes_decryption_remaining = aes_decryption_remaining[176:]
			aes_encoded = binascii.unhexlify(tmp).decode('utf-8')
			aes_decrypted = aes.aes_decrypt(aes_encoded, key, padding, block_size)
			data_outgoing_remaining = data_outgoing_remaining + aes_decrypted
			(to_send_str, data_outgoing_remaining) = aes.parse_output(data_outgoing_remaining)
			for i in range(len(to_send_str)):
				channel[s].send(to_send_str[i])
				print 'packet is sent to tcp client'
	a.put(aes_encryption_remaining)
	b.put(aes_decryption_remaining)
	c.put(data_incoming_remaining)
	d.put(data_outgoing_remaining)
	#return  data_incoming_remaining, aes_encryption_remaining, aes_decryption_remaining, data_outgoing_remaining            

def send_one_packet(s, data, channel, timing, start, addr, fwd_host, fwd_port, data_incoming_remaining, aes_encryption_remaining, aes_decryption_remaining, data_outgoing_remaining):
	# When there is data, check the time
	flag = 0
	one_time = timing.get()
	start_time = start.get()
	while flag == 0:
		# when time is right
		if time.time() - start_time > one_time:
			print '-' * 30
			print 'time is up'
			print time.time() - start_time
			# If there is data, send the correct contents
			if data != '':
				print 'send data!!!!!!'
				print data
				#channel[s].send(data)
				#server_on_recv(s, data, channel)
				server_on_recv(s, data, channel, addr, fwd_host, fwd_port, data_incoming_remaining, aes_encryption_remaining, aes_decryption_remaining, data_outgoing_remaining)
				data = data[len(data):]
			# Else, send an empty packet
			else:
				print 'send empty packet??????'
				channel[s].send('')
			start.put(time.time())
			flag = 1
     
def gen_time(mode, timing, start, a_list, b_list, c_list):
	while True:
		time.sleep(1)
		#timing.put(1)
		choice, output = read_hmm(start, 'ntp-' + mode + '.fsa')
		start = output
		#print 'gen one time'
		one_timing = map_label_to_value(a_list, b_list, c_list, choice)
		print one_timing
		timing.put(one_timing)
		#print timing.qsize()


def read_hmm(start, filename):
	tree = ET.parse(filename)
	root = tree.getroot()
	# Get all states and transitions
	state = []
	for child in root:
		for gdchild in child:
			#print gdchild.tag
			#print  gdchild.attrib['id']
			if gdchild.tag == 'e-state':
				state.append(gdchild.attrib['id'])
	# Given a start state
	choice = []
	prob = []
	end = []
	for child in root:
		for gdchild in child:
			if gdchild.tag == 'event' and gdchild.attrib['state1ID'] == start:
				choice.append(gdchild.attrib['name'])
				prob.append(gdchild.attrib['value'])
				end.append(gdchild.attrib['state2ID'])
	# Make decision
	rand = random.random()
	#print rand
	flag = 0
	sum_prob = [0] * len(prob)
	sum_prob[0] = float(prob[0])
	for i in range(1, len(prob)):
		sum_prob[i] = sum_prob[i-1] + float(prob[i])
	sum_prob[len(prob)-1] = 1
	for i in range(0, len(prob)-1):
		if rand > sum_prob[i] and rand < sum_prob[i+1]:
			output = i+1
			flag = 1
		if flag == 0:
			output = 0
	# Output the chosen label and output state
	return choice[output], end[output]

def read_file(filename):
	f = open(filename)
	line = f.readlines()
	f.close()
	data = [0.0] * len(line)
	for i in range(len(line)):
		data[i] = float(line[i].strip())
	return data

def map_label_to_value(a_list, b_list, c_list, choice):
	output = ''
	if choice == 'a':
		output = random.choice(a_list)
	if choice == 'b':
		output = random.choice(b_list)
	if choice == 'c':
		output = random.choice(c_list)
	return output               


if __name__ == '__main__':
	# Changing the buffer_size and delay, you can improve the speed and bandwidth.
	# But when buffer get to high or delay go too down, you can broke things
	buffer_size = 4096
	delay = 0.0001
	conn_host = ''
	conn_port = 10000
	fwd_host = ''
	fwd_port = 50000
	# AES parameter
	block_size =  16
	padding = '{'
	key_file = 'aes_key'
	# Generate AES key
	#key = aes.aes_gen_key(block_size, key_file)
	key = aes.aes_read_key(block_size, key_file)
	# Shared data between process
	#aes_encryption_remaining = ''
	#aes_decryption_remaining = ''
	#data_incoming_remaining = ''
	#data_outgoing_remaining = ''
	#data = ''
	#server = server_init(conn_host, conn_port)
	#server_recv_data(conn_host, conn_port, fwd_host, fwd_port, data, server)

	# Read into file
	mode = 'client'
	a_list = read_file('ntp-' + mode + '-pattern/a')
	b_list = read_file('ntp-' + mode + '-pattern/b')
	c_list = read_file('ntp-' + mode + '-pattern/c')
	start_state = '2'


	try:
		# Share timing between processes
		m = multiprocessing.Manager()
		timing = m.Queue()	
		# Share starting time between process
		s = multiprocessing.Manager()
		start = s.Queue()
		# share received data between processes
		d = multiprocessing.Manager()
		shared_data = d.Queue()
		# share parameter between process
		p1 = multiprocessing.Manager()
		aes_encryption_remaining = p1.Queue()
		p2 = multiprocessing.Manager()
		aes_decryption_remaining = p2.Queue()
		p3 = multiprocessing.Manager()
		data_incoming_remaining = p3.Queue()
		p4 = multiprocessing.Manager()
		data_outgoing_remaining = p4.Queue()
		aes_encryption_remaining.put('')
		aes_decryption_remaining.put('')
		data_incoming_remaining.put('')
		data_outgoing_remaining.put('')
		# One process to generate HMM timing
		print 'start generating timing now'
		hmm = multiprocessing.Process(target = gen_time, args = (mode, timing, start_state, a_list, b_list, c_list,))
		hmm.start()
		time.sleep(5)
		# One process to receive messages
		print 'Prepare the socket'
		start.put(time.time())
		server = server_init(conn_host, conn_port)
		rev = multiprocessing.Process(target = server_recv_data, args = (conn_host, conn_port, fwd_host, fwd_port, shared_data, server,timing, start, aes_encryption_remaining, aes_decryption_remaining, data_incoming_remaining, data_outgoing_remaining,))	
		rev.start()
		# One process to send messages based on timing
		#print 'start checking time!'
		#sd = multiprocessing.Process(target = check_time, args = (timing, start, shared_data,))	
		hmm.join()
		rev.join()
		#sd.join()

	except KeyboardInterrupt:
		print "Ctrl C - Stopping server"
		sys.exit(1)



	#try:
		#server.main_loop()
	#except KeyboardInterrupt:
		#print "Ctrl C - Stopping server"
		#sys.exit(1)



