#!/bin/env/python
# -*- encoding: utf-8 -*-
"""
===============================================================================
Experimental Camera Gyroscope
===============================================================================
author=gndctrl2mjrtm
-------------------------------------------------------------------------------
"""
from __future__ import print_function
from __future__ import division
import numpy as np
import argparse
import time
import cv2
import sys
import os

import config


"""
===============================================================================
Camera Gyroscope
===============================================================================
"""

class CameraGyroscope():

	def __init__(self):
		self.template_size = config.TEMPLATE_SIZE
		self.w_range       = config.CAMERA_HORIZONTAL_RANGE
		self.h_range       = config.CAMERA_VERTICAL_RANGE
    
    #--------------------------------------------------------------------------

	def template_crds(self,frame):
		# Get the size of the main frame
		w,h         = frame.shape[:2]
		w_mid,h_mid = int(w/2),int(h/2)
		tw_half     = int(self.template_size[0]/2)
		th_half     = int(self.template_size[1]/2)

		# Return the coordinates of the original template
		return [w_mid-tw_half,w_mid+tw_half,h_mid-th_half,h_mid+th_half]

	#--------------------------------------------------------------------------


	def find_template(self,template,image):
		"""Find the template from frame1 in frame2"""
		start_time = time.time()
		h,w = template.shape[:2]
		try:
			res = cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)

			__, __, __, top_left = cv2.minMaxLoc(res)
			bottom_right = (top_left[0]+ w,top_left[1]+h)

			if config.DISPLAY:
				cv2.rectangle(image,top_left, bottom_right, 255, 4)
			print("time elapsed: {}".format(time.time()-start_time))
		except:
			return None,image
		return bottom_right,image

	#--------------------------------------------------------------------------

	def angle_difference(self,dw,dh,w,h):
		"""Convert the difference in pixels to an angle difference"""
		w_angle = np.arctan(dw)
		h_angle = np.arctan(dh)
		return w_angle,h_angle

	#--------------------------------------------------------------------------

	def radian(self,angle):
		"""Convert angle to radian"""
		return (2*np.pi*angle)/360.

	#--------------------------------------------------------------------------

	def extract_templates(self,frame):
		# print(frame)
		tw = int(config.TEMPLATE_SIZE[0]/2)
		th = int(config.TEMPLATE_SIZE[1]/2)

		h,w = frame.shape[:2]
		w_interval = int(w/4)

		h_interval = int(h/4)
		origin_points = []
		for i in range(1,4,2):
			for j in range(1,4,2):
				origin_points.append((w_interval*i,h_interval*j))

		templates = [frame[y-th:y+th,x-tw:x+tw] for (x,y) in origin_points]
		base_points = [(x+tw,y+th) for (x,y) in origin_points]

		return templates,base_points


	#--------------------------------------------------------------------------

	def extract_angle_update(self,frame1,frame2,time1,time2):
		"""Get the angle change from the change in frames through
		 multiple subframes"""
		#if (len(frame1.shape)!=2):
		#	frame1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
		#if (len(frame2.shape)!=2):
		#	frame2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)

		h,w = frame1.shape[:2]		
		templates,base_points = self.extract_templates(frame1)

		delta_x = []
		delta_y = []
		for template,base in zip(templates,base_points):
			bottom_right,frame2 = self.find_template(template,frame2)
			if bottom_right:
				delta = np.subtract(bottom_right,base)
				delta_x.append(delta[0])
				delta_y.append(delta[1])

		#cv2.imshow('frame2',frame2)

		#cv2.waitKey(1)
				
		c = 3.0 # Needs to be properly fixed, temporary fix
		dx = np.average(delta_x)/c
		dy = np.average(delta_y)/c

		#dx,dy = self.angle_difference(dx,dy,w,h)
		return dx,dy


	#--------------------------------------------------------------------------


	def extract_angle(self,frame1,frame2,time1,time2):
		# OLD VERSION, 1 Subframe
		"""Get the angle change from the change in frames"""
		if (len(frame1.shape)!=2):
			frame1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
		if (len(frame2.shape)!=2):
			frame2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
		h,w = frame1.shape
		crds = self.template_crds(frame1)
		template = frame1[crds[0]:crds[1],crds[2]:crds[3]]

		b_right1 = (crds[3],crds[1])
		b_right2,frame_template = self.find_template(template,frame2)
		
		delta_x = b_right2[0]-b_right1[0]
		delta_y = b_right2[1]-b_right1[1]
		w,h = frame1.shape
		dw,dh = self.angle_difference(delta_x,delta_y,w,h)
		w_velocity = self.radian(dw/(time2-time1)) 

		print("(W) Radians per second: {}".format(w_velocity),file=sys.stderr)

		if config.DISPLAY:
			cv2.imshow("frame_template",frame_template)
			cv2.imshow("template",template) 
			cv2.imshow("frame2",frame2)

		return delta_x,delta_y




"""
===============================================================================
Main
===============================================================================
"""

def main():
	cg = CameraGyroscope()
	video_data = cv2.VideoCapture(0)
	while True:
		_,frame2 = video_data.read()
		time1 = time.time()
		# time.sleep(0.1)
		_,frame1 = video_data.read()

		frame2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
		frame2 = np.divide(frame2,np.mean(frame2))

		frame1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
		frame1 = np.divide(frame1,np.mean(frame1))


		time2 = time.time()
		cg.extract_angle_update(frame1,frame2,time1,time2)
		cv2.imshow("frame1",frame1)
		key = cv2.waitKey(1)
		if key == ord('q'):
			break
	cv2.destroyALlWindows()

if __name__ == "__main__":
	main()