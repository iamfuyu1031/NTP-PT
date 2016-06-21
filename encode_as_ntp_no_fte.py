from __future__ import division
import random, string
from Crypto.Cipher import AES
import base64
import os
import math
import binascii

def randomword(length):
	return ''.join(random.choice(string.lowercase+string.digits) for i in range(length))

def aes_encrypt(string, key, padding, block_size):
	# one-liner to sufficiently pad the text to be encrypted
	pad = lambda s: s + (block_size - len(s) % block_size) * padding
	# one-liners to encrypt/encode and decrypt/decode a string
	# encrypt with AES, encode with base64
	EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
	# create a cipher object using the random secret
	cipher = AES.new(key)
	# encode a string
	encoded = EncodeAES(cipher, string)
	return encoded

def convert_string_to_hex(string):
	hex_output = ''
	for i in range(len(string)):
		hex_output += hex(ord(string[i]))[2:].zfill(2)
	return hex_output

def cut_into_certain_chunk(encoded, size):
	len_of_chunk = int(math.ceil(len(encoded)/size))
	output = [''] * len_of_chunk
	for i in range(len_of_chunk):
		try:
			output[i] = encoded[i*size:(i+1)*size]
		except:
			output[i] = encoded[i*size:]
	return output

def map_chunk_to_ntp_field(one_chunk, position, field):
	# Convert the one_chunk value to hex
	int_value = int(one_chunk,16)
	# Random pick a value from the group
	picked_value = random.choice(field[int_value])
	# Convert the picked value into hex format
	picked_hex = convert_field_value_to_hex(picked_value)
	return picked_hex

def convert_field_value_to_hex(value):
	tmp = value.split('+')
	output = ''
	for i in range(len(tmp)):
		output += hex(int(tmp[i]))[2:].zfill(2)
	return str(output)

def map_fte_to_ntp(one_chunk, group, field):
	chunk = [''] * (len(group)-1)
	hex_output = ''
	for i in range(len(group)-1):
		chunk[i] = one_chunk[group[i]:group[i+1]]
		hex_output += map_chunk_to_ntp_field(chunk[i], i, field[i])
	return hex_output

def rewrite_output(output, folder, short_field):
	result = hex(int(random.choice(short_field[0])))[2:].zfill(2) + hex(int(random.choice(short_field[1])))[2:].zfill(2) + output
	return result

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

# Cut list into 16 chunks
def chunks(seq, size):
	newseq = []
	splitsize = 1.0/size*len(seq)
	for i in range(size):
		    newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
	return newseq

def transform_aes_into_ntp(hex_encoded):
	remaining = ''
	# NTP parameters
	folder = 'ntp_packet_field_short_client'
	long_byte_range = [44,45,46,50,54,58,66,74,82,90]
	short_byte_range = [42,43,44]
	group = [0,1,2,5,9,11,15,19,23,27]
	# Change the encoding into HEX
	#hex_encoded = convert_string_to_hex(aes_output)
	#hex_encoded = binascii.hexlify(aes_output.encode('utf-8'))
	# Cut into chunks of length 27
	chunk = cut_into_certain_chunk(hex_encoded, 27)
	# Transform into NTP
	long_field = retrieve_long_field(long_byte_range, folder)
	short_field = retrieve_short_field(short_byte_range, folder)
	output = []
	for i in range(len(chunk)):
		if len(chunk[i]) == 27:
			output.append(rewrite_output(map_fte_to_ntp(chunk[i], group, long_field), folder, short_field))
		else:
			#remaining += binascii.unhexlify(chunk[i]).decode('utf-8') 
			remaining += chunk[i]
	return output, remaining

# To satisfy the rate of data --> AES to be 63 --> 176, we have to buffer the data a little bit
def handle_data(old_data, target_size, data_remaining):
	output = []
	# Add the remaining data into the new data
	data = data_remaining + old_data
	data_remaining = ''
	# If the length is not enough
	if len(data) < target_size:
		data_remaining = data
	# If the length is enough to do AES
	else:
		chunk = cut_into_certain_chunk(data, target_size)
		for i in range(len(chunk)):
			if len(chunk[i]) == target_size:
				output.append(chunk[i])
			else:
				data_remaining += chunk[i]
	return output, data_remaining


if __name__ == '__main__':
	# AES Parameters
	block_size =  16
	padding = '{'

	# Input a random string
	input_str = randomword(63)
	# Do AES to the string
	key = os.urandom(block_size)
	aes_encoded = aes_encrypt(input_str, key, padding, block_size)
	# Change the encoding into HEX
	#hex_encoded = convert_string_to_hex(aes_encoded)
	hex_encoded = binascii.hexlify(aes_encoded.encode('utf-8'))
	# Cut into chunks of length 27
	chunk = cut_into_certain_chunk(hex_encoded, 27)
	# NTP parameters
	folder = 'ntp_packet_field_short_client'
	long_byte_range = [44,45,46,50,54,58,66,74,82,90]
	short_byte_range = [42,43,44]
	group = [0,1,2,5,9,11,15,19,23,27]
	long_field = retrieve_long_field(long_byte_range, folder)
	short_field = retrieve_short_field(short_byte_range, folder)
	output = []
	for i in range(len(chunk)):
		if len(chunk[i]) == 27:
			output.append(rewrite_output(map_fte_to_ntp(chunk[i], group, long_field), folder, short_field))
	print output





















