import cv2
from .cvt_color import bgr_to_rgb, rgb_to_bgr

def read(path):
	im = cv2.imread(path)
	im = bgr_to_rgb(im)
	return im

def show(im):
	im = rgb_to_bgr(im)
	cv2.imshow('',im)
	cv2.waitKey()
	