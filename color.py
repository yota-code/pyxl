#!/usr/bin/env python3

import numpy as np


yxb_to_rgb_mat = np.matrix([
	[11.031566901960783, -9.866943921568629, -0.16462299647058826]
	[-3.254147380392157, 4.418770392156863, -0.16462299647058826]
	[-3.6588512862745097, 2.7129230470588235, 1.9459282392156863]
])

xyb_bias = np.array([-0.0037930732552754493, -0.0037930732552754493, -0.0037930732552754493])
#  = -0.0037930732552754493	opsin_bias0
#  = -0.0037930732552754493	opsin_bias1
#  = -0.0037930732552754493	opsin_bias2
#  = 1-0.05465007330715401	quant_bias0
#  = 1-0.07005449891748593	quant_bias1
#  = 1-0.049935103337343655	quant_bias2
# quant_bias_numerator = 0.145	


def YXB_to_RGB(Y, X, B, intensity_target) :
	Lgamma = Y + X
	Mgamma = Y - X
	Sgamma = B

	itscale = 255 / intensity_target

	Lmix = ((np.pow(Lgamma - np.cbrt(xyb_bias[0])),3) + xyb_bias[0]) * itscale
	Mmix = ((np.pow(Mgamma - np.cbrt(xyb_bias[1])),3) + xyb_bias[1]) * itscale
	Smix = ((np.pow(Sgamma - np.cbrt(xyb_bias[2])),3) + xyb_bias[2]) * itscale
	
	R = yxb_to_rgb_mat[0][0] * Lmix + yxb_to_rgb_mat[0][1] * Mmix + yxb_to_rgb_mat[0][2] * Smix
	G = yxb_to_rgb_mat[1][0] * Lmix + yxb_to_rgb_mat[1][1] * Mmix + yxb_to_rgb_mat[1][2] * Smix
	B = yxb_to_rgb_mat[2][0] * Lmix + yxb_to_rgb_mat[2][1] * Mmix + yxb_to_rgb_mat[2][2] * Smix

	return R, G, B