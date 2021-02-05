import pygame
import math
import numpy as np
from pygame.locals import *

def set_g(dyn_objects, g):
    for obj in dyn_objects:
        dyn_objects[obj].set_g(g)

def set_air_den(dyn_objects, air_den):
    for obj in dyn_objects:
        dyn_objects[obj].set_air_den(air_den)

class Dynamic_object():
    def __init__(self, window, g, air_den, mass, colour):
        self.g = g
        self.window = window
        self.pos = np.array([0.0,0.0])
        self.vel = np.array([0.0,0.0])
        self.acc = np.array([0.0,self.g])
        self.mass = mass
        self.grabbed = False
        self.colour = colour
        self.co_rest = 0.85
        self.air_den = air_den

    def dynamics(self, frame_time):
        self.drag = (self.vel ** 2) * self.air_den / float(self.mass)
        
        if self.vel[0] > 0:
            self.drag[0] *= -1
        if self.vel[1] > 0:
            self.drag[1] *= -1

        self.acc = self.drag
        self.acc[1] += self.g
        self.vel += self.acc * frame_time
        self.pos += self.vel * frame_time

    def collision(self, resolution):
        if self.pos[1] >= resolution[1] - self.size/2 - 20:
            self.pos[1] = resolution[1] - self.size/2 - 20
            self.vel[1] = -self.vel[1] * self.co_rest

        elif self.pos[1] <= self.size/2 + 20:
            self.pos[1] = self.size/2 + 20
            self.vel[1] = -self.vel[1] * self.co_rest

        if self.pos[0] >= resolution[0] - self.size/2 - 20:
            self.pos[0] = resolution[0] - self.size/2 - 20
            self.vel[0] = -self.vel[0] * self.co_rest

        elif self.pos[0] <= self.size/2 + 20:
            self.pos[0] = self.size/2 + 20
            self.vel[0] = -self.vel[0] * self.co_rest
        

    def set_pos(self, pos):
        self.pos = np.array(pos)

    def set_vel(self, vel):
        self.vel = np.array(vel)

    def set_acc(self, acc):
        self.acc = np.array(acc)

    def set_g(self, g):
        self.g = g

    def set_air_density(self, air_den):
        self.air_den = air_den
    

class Static_object():
    def __init__(self, window, colour):
        self.window = window
        self.pos = np.array([0,0])
        self.colour = colour

    def set_pos(self, pos):
        self.pos = np.array(pos)


class Square(Dynamic_object):
    def __init__(self, window, g, air_den, mass, size, colour):
        super().__init__(window, g, air_den, mass, colour)
        self.size = size

    def render(self):
        pygame.draw.rect(self.window, self.colour, [self.pos[0] - self.size/2, self.pos[1] - self.size/2, self.size, self.size])
        

class Border(Static_object):
    def __init__(self, window, size, colour):
        super().__init__(window, colour)
        self.size = size

    def render(self):
        pygame.draw.rect(self.window, self.colour, [self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2, self.size[0], self.size[1]])
