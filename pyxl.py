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

	def __init__(self, byt:bytes) :
		self.byt = BytReader(byt)
		self.len = len(byt)

		self.process()

	def read_box(self) :
		"""
		a box is mode of a header and a payload
		the header is made of 
		- a 4 bytes, big endian, unsigned int which contains the total size of the box, including the header
		- a 4 bytes idendification code (usually as ASCII letters)
		- an optionnal 8 bytes, big endian, unsigned int which contains the extended size for boxes bigger than 2**32 bytes
		"""
		size = self.byt.read_ctyp('>L')[0]
		four = self.byt.read_bytes(4)
		if size == 1 :
			size = self.byt.read_ctyp('>Q')[0]
			head = 32
		else :
			head = 16
		start = self.byt.curs
		stop = start + size - head
		self.byt.seek_abs(stop)
		return four, slice(start, stop)

	def process(self) :
		if self.check_signature_box() :
			"""
			the file uses boxes, it is not a raw codestream
			"""
			assert self.check_filetype_box()

			while self.byt.curs < self.len - 16 :
				print(self.byt.curs)
				four, extract = self.read_box()
				match four :
					case b'jxlc' :
						self.decode_jxlc(extract)
					case _ :
						print(f"unknown fourcc:{four}:at{extract.start}")

	def check_signature_box(self) :
		"""
		If the signature box is present:
		- it is always at the start of the file
		- it means the file uses a containerized format instead of a raw codestream
		- the signature box is 12 bytes and hold this exact value:
			00 00 00 0C   4A 58 4C 20
			0D 0A 87 0A	
		"""
		self.byt.seek_abs(0)
		e = self.byt.read_bytes(12)
		z = e == self.signature_box
		print(f"signature box ... {disp(z, 'FOUND', 'NONE', e)}")
		return z

	def check_filetype_box(self) :
		"""
		The filetype box is always the second box
		It is 20 bytes and its value is always:
			00 00 00 14   66 74 79 70
			6A 78 6C 20   00 00 00 00
			6A 78 6C 20
		"""
		self.byt.seek_abs(12)
		e = self.byt.read_bytes(20)
		z = e == self.filetype_box
		print(f"filetype box ... {disp(z, 'FOUND', 'NONE', e)}")
		return z

	def decode_jxlc(self, extract) :
		print(self.byt[extract][:32])
		return

if __name__ == '__main__' :

	import sys

	byt = Path(sys.argv[1]).read_bytes()
	# bit = BitReader(byt)
	u = JxlLecter(byt)

