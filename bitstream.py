

class BitStream() :

	def __init__(self, data) :
		self.data = data
		self.curs = 0

	def __len__(self) :
		return len(self.data) * 8
	
	def bit_address(self, k) :
		return k // 8, 7 - k % 8

	def _get_range(self, k_slice) :
		o_start, b_start = self.bit_address(k_slice.start)
		o_stop, b_stop = self.bit_address(k_slice.stop)

		print("start:", k_slice.start, o_start, b_start)
		print("stop:", k_slice.stop, o_stop, b_stop)

		m_start = self.data[o_start] & ((1 << (b_start + 1)) - 1)

		print(f"{((1 << (b_start + 1)) - 1):b} {m_start:b}")

		if o_start == o_stop :
			print("RAAAH", m_start >> b_stop)
			return m_start >> b_stop
		
		return "TUTU"

		# return int.from_bytes(
		# 	self.data[o_start] & 1 << ((b_start + 1) - 1) + 
		# 	self.data[o_start:o_stop]
		# ) >> (7 - b_stop)

	def _get_bit(self, k_index) :
		o, b = self.bit_address(k_index)
		return 1 if (self.data[o] & 0x1 << (b)) else 0

	def __getitem__(self, key) :
		if isinstance(key, slice) :
			# return [self[ii] for ii in xrange(*key.indices(len(self)))]
			return self._get_range(key)
		elif isinstance(key, int) :
			if key < 0 : # Handle negative indices
				key += len(self)
			if key < 0 or key >= len(self):
				raise IndexError(f"The index {key} is out of range.")
			return self._get_bit(key) # Get the data from elsewhere
		else:
			raise TypeError("Invalid argument type.")
    
	def read_U32(self, ) :
		pass


if __name__ == '__main__' :
	c = b'\x80\x40\xFF\xC5'
	u = BitStream(c)

	for i in range(len(u)) :
		print(u[i], end=' - ')
	print()

	print(f"{u[8:12]:b}")
