#!/usr/bin/env python3

import struct

class BytReader() :
	"""
	hybrid reader, either by slice of as stream
	"""
	def __init__(self, data) :
		self.data = data
		self.curs = 0

	def seek_abs(self, n:int) :
		self.curs = n

	def seek_rel(self, n:int) :
		self.curs += n
			
	def read_ctyp(self, fmt, at=None) :
		u = struct.Struct(fmt)
		print(u, type(u))
		if at is None :
			s = u.unpack_from(self.data, self.curs)
			p = u.size
			self.seek_rel(p)
		else :
			s = u.unpack_from(self.data, at)
		return s

	def read_bytes(self, n, at=None) :
		if at is None :
			s = self.data[self.curs:self.curs+n]
			self.seek_rel(n)
			return s
		else :
			return self.data[at:at+n]
	
	def __getitem__(self, key) :
		return self.data[key]


class BitReader() :
	def __init__(self, data) :
		self.data = data
		self.curs = 0

	def seek(self, bitindex:int) :
		self.curs = bitindex

	def Un(self, n:int) :
		if not 1 <= n :
			raise ValueError
		m = self[self.curs:self.curs+n]
		self.curs += n
		return m

	def U32(self, * f_lst) :
		return f_lst[self.read_Un(2)]()

	def _reindex(self, i) :
		if i < 0 :
			i += len(self)
		if not 0 <= i < len(self) :
			raise IndexError(f"{i} not in [0; {len(self)}[")
		return i

	def __len__(self) :
		return len(self.data) * 8
	
	def read_bytes(self, n) :
		pass
		
	def bit_address(self, k) :
		return k // 8, k % 8

	def _get_bitslice(self, k_slice) :
		s_start, s_stop = self._reindex(k_slice.start), self._reindex(k_slice.stop)

		o_start, b_start = self.bit_address(s_start)
		o_stop, b_stop = self.bit_address(s_stop)

		# print(f"start: {k_slice.start} :: {o_start}.{b_start}")
		# print(f"stop: {k_slice.stop} :: {o_stop}.{b_stop}")

		# print(f"self.data[o_start] = {hex(self.data[o_start])}")
		# print(f"((1 << (7 - b_start + 1)) - 1) = {hex(((1 << (7 - b_start + 1)) - 1))}")
		# print(f"self.data[o_start+1:o_stop+1] = {self.data[o_start+1:o_stop+2]}")
		# print(f"""int.from_bytes(
		# 	(self.data[o_start] & ((1 << (7 - b_start + 1)) - 1)).to_bytes(1, byteorder='big') + self.data[o_start+1:o_stop+2],
		# 	byteorder='big'
		# ) = {int.from_bytes(
		# 	(self.data[o_start] & ((1 << (7 - b_start + 1)) - 1)).to_bytes(1, byteorder='big') + self.data[o_start+1:o_stop+1],
		# 	byteorder='big'
		# )}""")

		return int.from_bytes(
			(self.data[o_start] & ((1 << (7 - b_start + 1)) - 1)).to_bytes(1, byteorder='big') + self.data[o_start+1:o_stop+1],
			byteorder='big'
		) >> 8 - b_stop

	def _get_bitindex(self, k_index) :
		o, b = self.bit_address(k_index)
		return 1 if (self.data[o] & 0x1 << (7 - b)) else 0

	def __getitem__(self, key) :
		if isinstance(key, slice) :
			# return [self[ii] for ii in xrange(*key.indices(len(self)))]
			return self._get_bitslice(key)
		elif isinstance(key, int) :
			if key < 0 :
				key += len(self)
			if key < 0 or key >= len(self):
				raise IndexError(f"The index {key} is out of range.")
			return self._get_bitindex(key)
		else:
			raise TypeError("Invalid argument type.")
    


if __name__ == '__main__' :

	print(bin(BitStream(b'\x00\x71\xC0')[9:19]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:18]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:17]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:16]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:15]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:14]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:13]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:12]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:11]))
	print(bin(BitStream(b'\x00\x71\xC0')[9:10]))

	# c = b'\x80\x40\xFF\xC5'
	# u = BitStream(c)

	# for i in range(len(u)) :
	# 	print(u[i], end=' - ')
	# print()

	# print(f"{u[8:12]:b}")
