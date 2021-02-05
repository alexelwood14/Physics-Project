import pygame
import math
import numpy as np
import pygame_ui
import random
from pygame.locals import *

class boid():
    def __init__(self, window, colour, size, resolution, vision_range):
        self.window = window
        self.colour = colour
        self.size = size
        self.vision_range = vision_range
        self.col_range = vision_range / 5 * 2
        self.vision_arc = math.pi / 3
        self.detected_boids = []
        
        self.pos = np.array([random.random()*resolution[0], random.random()*resolution[1]])
        self.grid_coords = [int(self.pos[0] // self.vision_range), int(self.pos[1] // self.vision_range)]
      
        self.speed = 150.0
        self.vel = np.array([0.0,200.0])
        self.acc = np.array([0.0,0.0])
        
        self.ang_pos = random.random()*math.pi*2
        self.ang_vel = 0.0
        self.ang_acc = 0.0

        self.ang_vel_max = 8.0

        self.points_mat = np.array([[0, self.size],
                                    [self.size / 1.7, -self.size],
                                    [0, -self.size / 2],
                                    [-self.size / 1.7, -self.size]])
        
    def visible_boids(self, boids, grid):
        self.detected_boids = []
        direction = np.array([0,0])
        self.ang_vel = 0.0
        
        boids = []
        boids.extend(grid[self.grid_coords[0]][self.grid_coords[1]])
        
        if self.grid_coords[0] > 0:
            boids.extend(grid[self.grid_coords[0]-1][self.grid_coords[1]])
            if self.grid_coords[1] > 0:
                boids.extend(grid[self.grid_coords[0]-1][self.grid_coords[1]-1])
            if self.grid_coords[1] < len(grid[0])-1:
                boids.extend(grid[self.grid_coords[0]-1][self.grid_coords[1]+1])
            
        if self.grid_coords[0] < len(grid)-1:
            boids.extend(grid[self.grid_coords[0]+1][self.grid_coords[1]])
            if self.grid_coords[1] > 0:
                boids.extend(grid[self.grid_coords[0]+1][self.grid_coords[1]-1])
            if self.grid_coords[1] < len(grid[0])-1:
                boids.extend(grid[self.grid_coords[0]+1][self.grid_coords[1]+1])

        if self.grid_coords[1] > 0:
            boids.extend(grid[self.grid_coords[0]][self.grid_coords[1]-1])

        if self.grid_coords[1] < len(grid[0])-1:
            boids.extend(grid[self.grid_coords[0]][self.grid_coords[1]+1])
        
        for boid in boids:
            if boid != self:
                #calculate distance
                boid_pos = boid.get_pos()
                loc_vec = boid_pos - self.pos
                distance = np.sqrt((loc_vec).dot(loc_vec))
                if distance != 0 or (loc_vec[0] != 0.0 and loc_vec[1] != 0.0):

                    #calculate angle
                    temp = np.dot(self.vel, loc_vec) / distance / self.speed
                    if temp > 1:
                        temp = 1
                    elif temp < -1:
                        temp = -1
                    angle = math.acos(temp)

                    #check if in vision
                    if distance <= self.vision_range and abs(angle) <= self.vision_arc:
                        self.calc_ang_vel(boid, angle, distance)
                        self.detected_boids.append(boid)

    def calc_ang_vel(self, boid, angle, distance):
        boid_pos = boid.get_pos()
        if self.vel[0] != 0:
            line_height = self.vel[1] * boid_pos[0] / self.vel[0] + self.pos[1] - self.vel[1] * self.pos[0] / self.vel[0]

            if (boid_pos[1] < line_height and self.vel[0] <= 0) or (boid_pos[1] > line_height and self.vel[0] >= 0):
                self.ang_vel += angle * (math.log(distance / self.col_range, 1.15) - (distance/self.col_range/2)**2)
                    
            elif (boid_pos[1] > line_height and self.vel[0] <= 0) or (boid_pos[1] < line_height and self.vel[0] >= 0):
                self.ang_vel -= angle * (math.log(distance / self.col_range, 1.15) - (distance/self.col_range/2)**2)

        
    def dynamics(self, frame_time, resolution):
        #Angle Calculation
        if self.ang_vel > self.ang_vel_max:
            self.ang_vel = self.ang_vel_max
        elif self.ang_vel < -self.ang_vel_max:
            self.ang_vel = -self.ang_vel_max
            
        self.ang_vel += self.ang_acc * frame_time
        self.ang_pos += self.ang_vel * frame_time
        if self.ang_pos > 0:
            while self.ang_pos >= math.pi * 2:
                self.ang_pos -= math.pi*2
        else:
            while self.ang_pos <= 0:
                self.ang_pos += math.pi*2
        self.ang_mat = np.array([[math.cos(self.ang_pos), -math.sin(self.ang_pos)],
                                [math.sin(self.ang_pos), math.cos(self.ang_pos)]])

        #Displacement Calculation
        self.vel = np.matmul(self.ang_mat, np.array([0, self.speed]))
        self.pos += self.vel * frame_time

        #Move back into frame
        if self.pos[0] < 0:
            self.pos[0] = resolution[0]
        elif self.pos[0] > resolution[0]:
            self.pos[0] = 0

        if self.pos[1] < 0:
            self.pos[1] = resolution[1]
        elif self.pos[1] > resolution[1]:
            self.pos[1] = 0

        self.grid_coords = [int(self.pos[0] // self.vision_range), int(self.pos[1] // self.vision_range)]


    def render(self, colours, display_debug=False):
        #Debug Rendering
        if display_debug:
            pygame.draw.arc(self.window, colours["yellow"], [self.pos[0] - self.vision_range, self.pos[1] - self.vision_range,
                                                         self.vision_range*2, self.vision_range*2],
                        -self.ang_pos - (math.pi- self.vision_arc/2), -self.ang_pos - self.vision_arc/2)

            pygame.draw.line(self.window, colours["yellow"], [self.pos[0] + self.vision_range * math.cos(self.ang_pos + self.vision_arc /2),
                                                              self.pos[1] + self.vision_range * math.sin(self.ang_pos + self.vision_arc /2)],
                             [self.pos[0], self.pos[1]])
            pygame.draw.line(self.window, colours["yellow"], [self.pos[0] - self.vision_range * math.cos(self.ang_pos - self.vision_arc /2),
                                                              self.pos[1] - self.vision_range * math.sin(self.ang_pos - self.vision_arc /2)],
                             [self.pos[0], self.pos[1]])
            
            if len(self.detected_boids) > 0:
                self.colour = colours["green"]
                for boid in self.detected_boids:
                    loc_vec = boid.get_pos() - self.pos
                    if np.sqrt((loc_vec).dot(loc_vec)) < self.vision_range:
                        pygame.draw.line(self.window, colours["blue"], self.pos, boid.get_pos(), 3)
            else:
                self.colour = colours["red"]
        else:
            self.colour = colours["red"]

        #Normal Rendering
        points = np.matmul(self.ang_mat, np.transpose(self.points_mat))
        points = np.transpose(points)
        pygame.draw.polygon(self.window, self.colour, points + self.pos)


    def get_pos(self):
        return self.pos

    def get_grid_coords(self):
        return self.grid_coords


    def get_ang_pos(self):
        return self.ang_pos

def main():
    pass

if __name__ == "__main__":
    main()
