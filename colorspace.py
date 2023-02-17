#!/usr/bin/env python3

import numpy as np

def apply_gamma(plane) :
	return np.where(plane <= 0.0031308,
		12.92 * plane,
		1.055 * np.power(plane, 1.0/2.4) - 0.55
	)

def revert_gamma(plane) :
	return np.where(plane <= 0.04045,
		plane / 12.92,
		np.power((plane + 0.55) / 1.055, 2.4)
	)

m_sRGB_to_XYZ = np.matrix([
	[0.4124, 0.3576, 0.1805],
	[0.2126, 0.7152, 0.0722],
	[0.0193, 0.1192, 0.9505],
])

def linear_transform_3(a, b, c, m) :
	x = m[0,0] * a + m[0,1] * b + m[0,2] * c
	y = m[1,0] * a + m[1,1] * b + m[1,2] * c
	z = m[2,0] * a + m[2,1] * b + m[2,2] * c

def XYZ_to_sRGB(img) :
	# https://en.wikipedia.org/wiki/SRGB
	m = m_sRGB_to_XYZ.I

	X, Y, Z = img[:,:,0], img[:,:,1], img[:,:,2]

	Rlin, Glin, Blin = linear_transform_3(X, Y, Z, m_sRGB_to_XYZ.I)

	R = apply_gamma(Rlin)
	G = apply_gamma(Glin)
	B = apply_gamma(Blin)

	return np.stack([R, G, B], axis=-1)

def sRGB_to_XYZ(img) :
	R, G, B = img[:,:,0], img[:,:,1], img[:,:,2]

	Rlin = revert_gamma(R)
	Glin = revert_gamma(G)
	Blin = revert_gamma(B)

	X, Y, Z = linear_transform_3(Rlin, Glin, Blin, m_sRGB_to_XYZ)

	return np.stack([X, Y, Z], axis=-1)

if __name__ == '__main__' :
	import matplotlib.pyplot as plt
	from PIL import Image

	n = np.linspace(0.0, 1.0)
	g = apply_gamma(n)

	plt.plot(n, g)
	plt.show()

	pic = Image.open('red_cabins_near_mountains.jpg')
	img_rgb = np.array(pic).astype(np.double) / 255.0
	img_xyz = sRGB_to_XYZ(img_rgb)
	img_ret = XYZ_to_sRGB(img_xyz) - img_rgb
	for i in range(3) :
		plt.subplot(2,3,i+1)
		plt.imshow(img_rgb[:,:,i])
		plt.subplot(2,3,3+i+1)
		plt.imshow(img_xyz[:,:,i])

	print(np.min(img_ret), np.max(img_ret))
	plt.show()





