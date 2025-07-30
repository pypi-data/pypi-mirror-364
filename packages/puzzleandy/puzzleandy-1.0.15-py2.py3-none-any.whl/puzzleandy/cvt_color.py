import cv2

def bgr_to_rgb(bgr):
	rgb = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
	return rgb

def rgb_to_bgr(bgr):
	bgr = cv2.cvtColor(bgr,cv2.COLOR_RGB2BGR)
	return bgr

def rgb_to_gray(rgb):
	gray = cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
	return gray