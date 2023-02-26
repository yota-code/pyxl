#!/usr/bin/env python3

import io
import math
import sys

import numpy as np

from PIL import Image

from cc_pathlib import Path

def RGBu8_to_YCoCgu10(src_u8) :
	src_i16 = src_u8.astype(np.int16)

	# for i, m in enumerate('RGB') :
	# 	print(f"RGBu8_to_YCoCgu10 :: {m} in [{src_i16[:,:,i].min()}, {src_i16[:,:,i].max()}]")
	# 	print(src_i16[:,:,i])

	R, G, B = src_i16[:,:,0], src_i16[:,:,1], src_i16[:,:,2]
	Y, Co, Cg = R + 2*G + B, 2*R - 2*B, -R + 2*G - B

	# convert to magnitude + sign
	Co = np.where(Co >= 0, Co, -Co & 0x200)
	Cg = np.where(Cg >= 0, Cg, -Cg & 0x200)

	dst_i16 = np.stack((Y, Co, Cg), axis=-1)
	# for i, m in enumerate(['Y ', 'Co', 'Cg']) :
	# 	print(f"RGBu8_to_YCoCgu10 :: {m} in [{dst_i16[:,:,i].min()}, {dst_i16[:,:,i].max()}]")
	# 	print(dst_i16[:,:,i])

	return dst_i16

def YCoCgu10_to_RGBu8(src_i16) :

	# for i, m in enumerate(['Y ', 'Co', 'Cg']) :
	# 	print(f"YCoCgu10_to_RGBu8 :: {m} in [{src_i16[:,:,i].min()}, {src_i16[:,:,i].max()}]")
	# 	print(src_i16[:,:,i])

	Y, Co, Cg = src_i16[:,:,0], src_i16[:,:,1], src_i16[:,:,2]

	# convert from magnitude + sign
	Co = np.where(Co & 0x200, -(Co & 0x1FF), Co & 0x1FF)
	Cg = np.where(Cg & 0x200, -(Cg & 0x1FF), Cg & 0x1FF)

	R, G, B = (Y + Co - Cg) // 4, ((Y + Cg)) // 4, ((Y - Co - Cg)) // 4

	dst_i16 = np.stack((R, G, B), axis=-1)
	# for i, m in enumerate('RGB') :
	# 	print(f"RGBu8_to_YCoCgu10 :: {m} in [{dst_i16[:,:,i].min()}, {dst_i16[:,:,i].max()}]")
	# 	print(dst_i16[:,:,i])

	return dst_i16.astype(np.uint8)

def YCoCgu10_to_dbil(src_YCoCg) :
	height, width, channel = src_YCoCg.shape
	depth = 10

	dst_YCoCg = list()

	dst_YCoCg.append(height.to_bytes(2, byteorder='big'))
	dst_YCoCg.append(width.to_bytes(2, byteorder='big'))

	u = 0
	n = 0
	for d in reversed(range(depth)) :
		m = 0x1 << d
		for h in range(height) :
			for w in range(width) :
				for c in range(channel) :
					p = src_YCoCg[h, w, c]
					b = int((p & m) != 0)
					# if b :
					# 	print("*" if b else " ", h, w, c, d, (9 - d) * (3 * width * height) + h * (3 * width) + w * 3 + c, sep='\t')
					u = u * 2 + b
					n += 1
					if n == 32 :
						z = u.to_bytes(4, byteorder='big')
						# if u :
						# 	print(f">>> {u:032b} {z} {len(z)}")
						dst_YCoCg.append(z)
						n = 0
						u = 0
	if n != 0 :
		u <<= 32 - n
		z = u.to_bytes(4, byteorder='big')
		# if u :
		# 	print(f">>> {u:032b} {z} {len(z)}")
		dst_YCoCg.append(z)

	return b''.join(dst_YCoCg)

def dbil_to_YCoCg10(src_debil) :
		
	fid = io.BytesIO(src_debil)

	height = int.from_bytes(fid.read(2), byteorder='big')
	width = int.from_bytes(fid.read(2), byteorder='big')

	dst_YCoCg = np.zeros((height, width, 3), dtype=np.int16)

	dst_YCoCg[:,:,0] = 0x2cc

	h, w, c, d = 0, 0, 0, 9
	while True :
		z = fid.read(4)
		if len(z) :
			u = int.from_bytes(z, byteorder='big')
			# if u :
			# 	print(f">>> {u:032b} {z} {len(z)}")
			for i in range(32) :
				try :
					if (u & 0x80000000) :
						dst_YCoCg[h, w, c] |= 1 << d
					else :
						dst_YCoCg[h, w, c] &= ~(1 << d)
					# if b :
					# 	print("*" if b else " ", h, w, c, d, (9 - d) * (3 * width * height) + h * (3 * width) + w * 3 + c, sep='\t')
					c += 1
					if c == 3 :
						c = 0
						w += 1
					if w == width :
						w = 0
						h += 1
					if h == height :
						h = 0
						d -= 1
				except :
					break
				u <<= 1
		else :
			break

	return dst_YCoCg

def img_to_dbil(src_pth, dst_pth) :
	src_RGB = np.array(Image.open(src_pth))
	src_YCoCg = RGBu8_to_YCoCgu10(src_RGB)
	dst_debil = YCoCgu10_to_dbil(src_YCoCg)
	dst_pth.write_bytes(dst_debil)

def dbil_to_img(src_pth, dst_pth, limit=None) :
	src_debil = src_pth.read_bytes()

	fid = io.BytesIO(src_debil)

	height = int.from_bytes(fid.read(2), byteorder='big')
	width = int.from_bytes(fid.read(2), byteorder='big')

	if isinstance(limit, float) :
		limit = int(round(len(src_debil) * limit))
	
	if limit is not None :
		limit = max(6*(height * width)//16, limit)
		print(limit, 6*(height * width)//16, len(src_debil))
		src_debil = src_debil[:limit]

	dst_YCoCg = dbil_to_YCoCg10(src_debil)
	dst_RGB = YCoCgu10_to_RGBu8(dst_YCoCg)
	Image.fromarray(dst_RGB).save(dst_pth)

if __name__ == '__main__' :

	orig_pth = Path(sys.argv[1]).resolve()
	dbil_pth = orig_pth.with_suffix('.dbil')
	chck_pth = orig_pth.with_suffix('.check.png')

	img_to_dbil(orig_pth, dbil_pth)
	dbil_to_img(dbil_pth, chck_pth, 0.2)
