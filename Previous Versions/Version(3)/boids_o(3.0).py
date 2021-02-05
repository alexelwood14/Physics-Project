import pygame
import math
import numpy as np
import pygame_ui
import random
from pygame.locals import *

class boid():
    def __init__(self, window, colour, size, resolution, vision_range, pos, ang_vel=0.0):
        self.window = window
##        self.pos = np.array([random.random()*resolution[0], random.random()*resolution[1]])
        self.pos = np.array(pos)
##        self.vel = np.array([0.0,-200.0])
        self.vel = np.array([0.0,0.0])
        self.acc = np.array([0.0,0.0])
##        self.ang_pos = random.random()*math.pi*2
        self.ang_pos = 0.0
        self.ang_vel = ang_vel
        self.ang_acc = 0.0
        self.ang_mat = np.array([[math.cos(self.ang_pos), math.sin(self.ang_pos)],
                                [-math.sin(self.ang_pos), math.cos(self.ang_pos)]])

        self.colour = colour
        self.size = size
        self.vision_range = vision_range

        self.points_mat = np.array([[0, -self.size],
                                    [self.size / 1.7, self.size],
                                    [0, self.size / 2],
                                    [-self.size / 1.7, self.size]])

    def visible_boids(self, boids, colours):
        visible_boids = []
        seeing_boid = False
        for boid in boids:
            if boid != self:
                #calculate disntance
                boid_pos = boid.get_pos()
                loc_vec = boid_pos - self.pos
                distance = np.sqrt((loc_vec).dot(loc_vec))

                #find if in front of behind
                direction = np.matmul(self.ang_mat, np.array([1,0]))
                line_point = (direction[1]/direction[0]) * (boid_pos[0] - self.pos[0]) + self.pos[1]
                if distance < self.vision_range and (boid_pos[1] < line_point and (self.ang_pos < math.pi/2 or self.ang_pos > math.pi * 3/2) or
                    boid_pos[1] > line_point and (self.ang_pos > math.pi/2 or self.ang_pos < math.pi * 3/2)):
                        seeing_boid = True
                #calculate angle
                

        #visual demonstration
        if seeing_boid:
            self.colour = colours["green"]
        else:
            self.colour = colours["red"]

        
        
    def dynamics(self, frame_time, resolution):
        #Angle Calculation
##        self.ang_acc = (random.random() - 0.5) * math.pi
        self.ang_vel += self.ang_acc * frame_time
        self.ang_pos += self.ang_vel * frame_time
        if self.ang_pos > 0:
            while self.ang_pos >= math.pi:
                self.ang_pos -= math.pi*2
        else:
            while self.ang_pos <= -math.pi:
                self.ang_pos += math.pi*2
        self.ang_mat = np.array([[math.cos(self.ang_pos), math.sin(self.ang_pos)],
                                [-math.sin(self.ang_pos), math.cos(self.ang_pos)]])

        #Displacement Calculation
        self.vel_trans = np.matmul(self.ang_mat, self.vel)
        self.pos += self.vel_trans * frame_time

        #Move back into frame
        if self.pos[0] < 0:
            self.pos[0] = resolution[0]
        elif self.pos[0] > resolution[0]:
            self.pos[0] = 0

        if self.pos[1] < 0:
            self.pos[1] = resolution[1]
        elif self.pos[1] > resolution[1]:
            self.pos[1] = 0

    def render_arc(self, colours, vision_range):
        pygame.draw.arc(self.window, colours["yellow"], [self.pos[0] - vision_range, self.pos[1] - vision_range, vision_range*2, vision_range*2],
                        self.ang_pos, self.ang_pos + math.pi)
        pygame.draw.line(self.window, colours["yellow"], [self.pos[0] + 200*math.sin(self.ang_pos + math.pi/2), self.pos[1] + 200*math.cos(self.ang_pos + math.pi/2)],
                         [self.pos[0] - 200*math.sin(self.ang_pos + math.pi/2), self.pos[1] - 200*math.cos(self.ang_pos + math.pi/2)])

    def render(self):
        points = np.matmul(self.ang_mat, np.transpose(self.points_mat))
        points = np.transpose(points)
        pygame.draw.polygon(self.window, self.colour, points + self.pos)
##        print(self.ang_pos)

    def get_pos(self):
        return self.pos

    def get_ang_pos(self):
        return self.ang_pos

def main():
    pass

if __name__ == "__main__":
    main()
