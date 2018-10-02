#!/bin/env/python
# -*- encoding: utf-8 -*-
"""
===============================================================================

===============================================================================
"""
from __future__ import print_function
from __future__ import division
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
        _,frame2 = video_data.read()
        time1  = time.time()

        _,frame1 = video_data.read()
        time2  = time.time()


        frame2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
        #frame2 = np.subtract(frame2,np.mean(frame2))

        frame1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
        #frame1 = np.subtract(frame1,np.mean(frame1))

        print(frame1)
        print(frame2)

        dx,dy  = cg.extract_angle_update(frame1,frame2,time1,time2)

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


if __name__ == "__main__":
    main()