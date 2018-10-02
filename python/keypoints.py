#!/bin/env/python
# -*- encoding: utf-8 -*-
"""
===============================================================================

===============================================================================
"""
from matplotlib import pyplot as plt
import numpy as np
import argparse
import pygame
import time
import cv2
import sys
import os

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import config

from camera_gyro import CameraGyroscope


"""
===============================================================================

===============================================================================
"""

verticies = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
    )

colors = (
    (0,0,0),
    (0,0,0),
    (0,0,0),
    (0,0,1),
    (0,0,1),
    (0,0,1),
    (0,0,0),
    (0,0,0),
    (0,0,0),
    (0,0,0),
    (0,0,0),
    (0,0,0)
    )

def Cube():
    glBegin(GL_QUADS)
    for surface in surfaces:
        x = 0
        for vertex in surface:
            x+=1
            glColor3fv(colors[x])
            glVertex3fv(verticies[vertex])
    glEnd()

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()

"""
===============================================================================

===============================================================================
"""



def main():
    orb = cv2.ORB_create()

    cg = CameraGyroscope()
    video_data = cv2.VideoCapture(0)
    pygame.init()

    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0.0,0.0,-7)

    current_x_angle = 0
    current_y_angle = 0
    while True:
        _,img1 = video_data.read()
        #time1  = time.time()

        _,img2 = video_data.read()
        #time2  = time.time()


        kp1, des1 = orb.detectAndCompute(img1,None)
        kp2, des2 = orb.detectAndCompute(img2,None)


        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        matches = bf.match(des1,des2)

        index = [n.trainIdx for n in matches]
        qindex = [n.queryIdx for n in matches]

        print('-'*80)

        n_matches = len(index)
        vectors = [np.subtract(kp2[index[i]].pt,kp1[qindex[i]].pt) for i in range(n_matches)]
        vectors = np.asarray(vectors)

        print(np.mean(vectors,axis=0))

        img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches,None,flags=2)


        dx,dy = -np.mean(vectors,axis=0)/(2*np.pi)
        #dx,dy  = cg.extract_angle_update(frame1,frame2,time1,time2)

        img3 = cv2.resize(img3,(600,300))


        cv2.imshow('img3',img3)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        current_y_angle += dy
        current_x_angle += dx
        print(current_x_angle,current_y_angle)
        glRotatef(-int(dx),0, 1, 0)
        glRotatef(int(dy),1, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        Cube()

        pygame.display.flip()
        pygame.time.wait(1)

        cv2.waitKey(1)


    '''
    video_data = cv2.VideoCapture(0)


    time.sleep(0.5)

    while True:
        _,img1 = video_data.read()
        _,img2 = video_data.read() 

        kp1, des1 = orb.detectAndCompute(img1,None)
        kp2, des2 = orb.detectAndCompute(img2,None)


        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        matches = bf.match(des1,des2)

        index = [n.trainIdx for n in matches]
        qindex = [n.queryIdx for n in matches]

        print('-'*80)

        n_matches = len(index)
        vectors = [np.subtract(kp2[index[i]].pt,kp1[qindex[i]].pt) for i in range(n_matches)]
        vectors = np.asarray(vectors)

        print(np.mean(vectors,axis=0))

        img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches,None,flags=2)

        img3 = cv2.resize(img3,(600,300))


        cv2.imshow('img3',img3)

        cv2.waitKey(1)'''


if __name__ == "__main__":
    main()


