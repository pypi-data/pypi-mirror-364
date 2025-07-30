from coloraide import Color
import numpy as np
from .cvt_color import rgb_to_gray

def gmap(im,interp):
	gray_vals = np.linspace(0,1,256)
	rgb_colors = np.empty((256,3),np.uint8)
	for i in range(256):
		rgb_color = interp(gray_vals[i])
		rgb_color = np.array(rgb_color)
		rgb_color = rgb_color[:3]
		rgb_color = np.array(rgb_color*255,np.uint8)
		rgb_colors[i] = rgb_color
	gray_im = rgb_to_gray(im)	
	rgb_im = rgb_colors[gray_im]
	return rgb_im

def black_to_red(im):
	interp = Color.interpolate([
		'black',
		'red'
		],space='srgb')
	im = gmap(im,interp)
	return im