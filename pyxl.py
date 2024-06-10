#!/usr/bin/env python3

from pathlib import Path

from bstream import BitReader, BytReader

def disp(z, ok="OK", ko="KO", extra='') :
	if z :
		s = "\x1b[32m" + ok + "\x1b[m"
	else :
		s = "\x1b[31m" + ko + "\x1b[m"
	if extra and not z :
		s += f" ({extra})"
	return s

class JxlLecter() :
	signature_box = b'\0\0\0\x0cJXL \r\n\x87\n'
	filetype_box = b'\0\0\0\x14ftypjxl \0\0\0\0jxl '

	def __init__(self, byt) :
		self.byt = BytReader(byt)

		self.process()

	def read_box(self) :
		"""
		a box header is made of 
		- a 4 bytes, big endian, unsigned int which contains the total size of the box, including this header
		- a 4 bytes idendification code (usually as ASCII letters)
		- an optionnal 8 bytes, big endian, unsigned int which contains the extended size for boxes bigger than 2**32 bytes
		"""
		zero = self.byt.curs
		size = self.byt.read_ctyp('>L')
		four = self.byt.read_bytes(4)
		if size == 1 :
			size = self.byt.read_ctyp('>Q')
		start = self.byt.curs
		stop = size - (start - zero)
		return four, slice(start, stop)

	def process(self) :
		if self.check_signature_box() :
			"""
			the file uses boxes, it is not a raw codestream
			"""
			assert self.check_filetype_box()

			i = 32
			while i < 1000 :
				box_size = struct.self.byt[i:i+4]
				i += 4
				match m :
					case b'jxll' :
						i = self.decode_jxll(i)
					case _ :
						print("unknown dispatcher", " ".join(hex(i) for i in m))
				break

	def check_signature_box(self) :
		"""
		If the signature box is present:
		- it is always at the start of the file
		- it means the file uses a containerized format instead of a raw codestream
		The signature box is 12 bytes and hold this exact value:
			00 00 00 0C 4A 58 4C 20
			0D 0A 87 0A	
		"""
		e = self.byt[0:12]
		z = e == self.signature_box
		print(f"signature box ... {disp(z, 'FOUND', 'NONE', e)}")
		return z

	def check_filetype_box(self) :
		"""
		The filetype box is always the second box
		It is 20 bytes and its value is always:
			00 00 00 14 66 74 79 70
			6A 78 6C 20 00 00 00 00
			6A 78 6C 20
		"""
		e = self.byt[12:32]
		z = e == self.filetype_box
		print(f"filetype box ... {disp(z, 'FOUND', 'NONE', e)}")
		return z

	def decode_jxl(self, i) :
		print(self.byt[i:i+1])
		return i + 1

if __name__ == '__main__' :

	import sys

	byt = Path(sys.argv[1]).read_bytes()
	# bit = BitReader(byt)
	u = JxlLecter(byt)

