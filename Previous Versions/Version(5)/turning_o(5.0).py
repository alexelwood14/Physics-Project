import pygame
import math
import numpy as np
from pygame.locals import *

class Wheel():
    def __init__(self, window, colour, pos, size, front=False):
        self.window = window
        self.colour = colour
        self.size = size
        self.front = front

        self.pos = np.array(pos)

        self.ang = 0.0
        self.mat = np.array([[math.cos(self.ang), -math.sin(self.ang)],
                                [math.sin(self.ang), math.cos(self.ang)]])

        self.points_mat = np.array([[-self.size / 2, -self.size],
                                    [self.size / 2, -self.size],
                                    [self.size / 2, self.size],
                                    [-self.size / 2, self.size]])

    def render(self):
        if self.front:
            points = np.matmul(self.mat, np.transpose(self.points_mat))
            points = np.transpose(points)
            pygame.draw.polygon(self.window, self.colour, points + self.pos)
        else:
            pygame.draw.polygon(self.window, self.colour, self.points_mat + self.pos)


    def set_pos(self, pos):
        self.pos = pos

    def set_ang(self, ang):
        self.ang = ang
        self.mat = np.array([[math.cos(self.ang), -math.sin(self.ang)],
                                [math.sin(self.ang), math.cos(self.ang)]])
        

class Car():
    def __init__(self, window, colours, pos, size):
        self.window = window
        self.colours = colours
        self.size = size

        self.pos = np.array(pos)
        self.speed = 0.0
        self.vel = np.array([0.0,0.0])
        self.acc = 0.0
        self.term_vel = 10 

        self.wheel_vel = 0.0
        self.wheel_ang = 0.0
        self.max_wheel_ang = math.pi/6
        self.wheel_mat = np.array([[math.cos(self.wheel_ang), -math.sin(self.wheel_ang)],
                                [math.sin(self.wheel_ang), math.cos(self.wheel_ang)]])
        self.wheel_normal = np.array([[1.0], [0.0]])

        self.points_mat = np.array([[-self.size, -self.size*2.5],
                                    [self.size, -self.size*2.5],
                                    [self.size, self.size*2.5],
                                    [-self.size, self.size*2.5]])

        self.font_axel = np.array([self.pos[0], self.pos[1]  + self.size * 1.6])
        self.rear_axel = np.array([self.pos[0], self.pos[1]  - self.size * 1.6])

        self.wheels = []
        self.wheels.append(Wheel(window, colours["grey"], [self.pos[0] - self.size, self.pos[1] - self.size * 1.6], size / 3))
        self.wheels.append(Wheel(window, colours["grey"], [self.pos[0] + self.size, self.pos[1] - self.size * 1.6], size / 3))
        self.wheels.append(Wheel(window, colours["grey"], [self.pos[0] + self.size, self.pos[1] + self.size * 1.6], size / 3, True))
        self.wheels.append(Wheel(window, colours["grey"], [self.pos[0] - self.size, self.pos[1] + self.size * 1.6], size / 3, True))
            

    def dynamics(self, frame_time):
        pressed = pygame.key.get_pressed()
        
        #Translation
        if pressed[pygame.K_w] and not pressed[pygame.K_s]:
            self.acc = 100
        elif not pressed[pygame.K_w] and pressed[pygame.K_s]:
            self.acc = -100
        else:
            if self.vel[1] > 0.0001:
                self.acc = -50
            elif self.vel[1] < 0.0001:
                self.acc = 50
            else:
                self.acc = 0
                
        self.vel[1] += self.acc * frame_time
        self.pos += self.vel * frame_time

        self.wheels[0].set_pos([self.pos[0] - self.size, self.pos[1] - self.size * 1.6])
        self.wheels[1].set_pos([self.pos[0] + self.size, self.pos[1] - self.size * 1.6])
        self.wheels[2].set_pos([self.pos[0] + self.size, self.pos[1] + self.size * 1.6])
        self.wheels[3].set_pos([self.pos[0] - self.size, self.pos[1] + self.size * 1.6])

        #Rotation
        if (pressed[pygame.K_a] and not pressed[pygame.K_d]) or (not pressed[pygame.K_a] and pressed[pygame.K_d]):
            if pressed[pygame.K_a] and not pressed[pygame.K_d]:
                self.wheel_vel = -2
            elif not pressed[pygame.K_a] and pressed[pygame.K_d]:
                self.wheel_vel = 2
            
        else:
            if self.wheel_ang > 0.01:
                self.wheel_vel = -2
            elif self.wheel_ang < 0.01:
                self.wheel_vel = 2
            else:
                self.wheel_vel = 0

        #Rotation Angle
        self.wheel_ang += self.wheel_vel * frame_time
        if self.wheel_ang > self.max_wheel_ang:
            self.wheel_ang = self.max_wheel_ang
        elif self.wheel_ang < -self.max_wheel_ang:
            self.wheel_ang = -self.max_wheel_ang

        for wheel in self.wheels:
            wheel.set_ang(self.wheel_ang) 


    def render(self):
        for wheel in self.wheels:
            wheel.render()
            
        points = np.matmul(self.wheel_mat, np.transpose(self.points_mat))
        points = np.transpose(points)
        pygame.draw.polygon(self.window, self.colours["red"], points + self.pos)

        
        
#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
