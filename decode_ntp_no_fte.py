from __future__ import division
import os

# Cut list into 16 chunks
def chunks(seq, size):
	newseq = []
	splitsize = 1.0/size*len(seq)
	for i in range(size):
		newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
	return newseq


def retrieve_long_field(long_byte_range, folder):
	bin_size = [1,1,3,4,2,4,4,4,4]
	working_dir = os.path.dirname(os.path.realpath(__file__))
	filename = [''] * (len(long_byte_range)-1)
	field = [[] for i in range(len(long_byte_range)-1)]
	for i in range(len(long_byte_range)-1):
		filename[i] = str(long_byte_range[i]) + '-' + str(long_byte_range[i+1])
		f = open(working_dir + '/' + folder + '/' + filename[i])
		line = f.readlines()
		f.close()
		data = [''] * len(line)
		for j in range(len(line)):
			data[j] = line[j].strip()
		field[i]+=chunks(data, 16 ** bin_size[i])
	return field

def retrieve_short_field(long_byte_range, folder):
	working_dir = os.path.dirname(os.path.realpath(__file__))
	filename = [''] * (len(long_byte_range)-1)
	field = [[] for i in range(len(long_byte_range)-1)]
	for i in range(len(long_byte_range)-1):
		filename[i] = str(long_byte_range[i]) + '-' + str(long_byte_range[i+1])
		f = open(working_dir + '/' + folder + '/' + filename[i])
		line = f.readlines()
		f.close()
		for j in range(len(line)):
			field[i].append(line[j].strip())
	return field	

# Search for index in a 2D list, return the index of group
def index_2d(myList, v):
    for i, x in enumerate(myList):
        if v in x:
            return i



def map_ntp_to_fte(chunk, position, long_field, bin_size):
	# Convert the chunk into format with '+'
	result = ''
	if len(chunk) == 2:
		result = str(int(chunk,16))
	else:
		for i in range(0, len(chunk), 2):
			result += str(int(chunk[i:i+2],16)) + '+'
		result = result[:-1]
	# serach for index
	index = index_2d(long_field, result)
	# Convert it to hex
	hex_index = hex(index)[2:].zfill(bin_size)
	return hex_index


def rewrite_input(result, long_byte_range,bin_size, long_field):
	# Remove the first 2 bytes
	short = result[4:]
	# Cut it into correct chunks
	chunk = [''] * (len(long_byte_range)-1)
	hex_index = [''] * (len(long_byte_range)-1)
	for i in range(len(long_byte_range)-1):
		chunk[i] = short[(long_byte_range[i]-44)*2:(long_byte_range[i+1]-44)*2]
		hex_index[i] = map_ntp_to_fte(chunk[i], i, long_field[i], bin_size[i])
	return hex_index

# Cut into slices
def cut(data, size):
	chunk = [''] * (int(len(data)/size))
	for i in range(int(len(data)/size)):
		chunk[i] = data[i*size:(i+1)*size]
	return chunk

def decode_string_as_ntp(data):
	# Initial parameters
	folder = 'ntp_packet_field_short_client'
	long_byte_range = [44,45,46,50,54,58,66,74,82,90]
	short_byte_range = [42,43,44]
	bin_size = [1,1,3,4,2,4,4,4,4]	
	group = [0,1,2,5,9,11,15,19,23,27]
	length = 450
	regex = '^[0-9a-f]+$'
	# Read into all possible values for each field (only consider field with more than 16 observations)
	long_field = retrieve_long_field(long_byte_range, folder)
	short_field = retrieve_short_field(short_byte_range, folder)
	hex_index = []
	for i in range(len(data)):
		hex_index += rewrite_input(data[i], long_byte_range, bin_size, long_field)
	output = ''.join(hex_index)
	return output

def recover_ntp_into_aes(data):
	# Initial parameters
	folder = 'ntp_packet_field_short_client'
	long_byte_range = [44,45,46,50,54,58,66,74,82,90]
	short_byte_range = [42,43,44]
	bin_size = [1,1,3,4,2,4,4,4,4]	
	group = [0,1,2,5,9,11,15,19,23,27]
	length = 450
	regex = '^[0-9a-f]+$'
	# Read into all possible values for each field (only consider field with more than 16 observations)
	long_field = retrieve_long_field(long_byte_range, folder)
	short_field = retrieve_short_field(short_byte_range, folder)
	hex_index = rewrite_input(data, long_byte_range, bin_size, long_field)
	output = ''.join(hex_index)
	return output

if __name__ == '__main__':
	# Read into the encoded result from file
	f = open('ntp-result')
	line = f.readlines()
	f.close()
	raw_string = line[0]
	chunk_size = 96
	chunk = [''] * int(len(raw_string)/chunk_size)
	for i in range(len(chunk)):
		chunk[i] = raw_string[i*chunk_size:(i+1)*chunk_size]
	output = decode_string_as_ntp(chunk)
	print output

