import pygame
import math
import numpy as np
from pygame.locals import *

class Wheel():
    def __init__(self, window, colour, pos, size):
        self.window = window
        self.colour = colour
        self.size = size

        self.pos = np.array(pos)

        self.ang = 0.0
        self.mat = np.array([[math.cos(self.ang), -math.sin(self.ang)],
                                [math.sin(self.ang), math.cos(self.ang)]])

        self.points_mat = np.array([[-self.size / 2, -self.size],
                                    [self.size / 2, -self.size],
                                    [self.size / 2, self.size],
                                    [-self.size / 2, self.size]])

    def render(self):
        points = np.matmul(self.mat, np.transpose(self.points_mat))
        points = np.transpose(points)
        pygame.draw.polygon(self.window, self.colour, points + self.pos)


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
        self.term_speed = 400

        self.ang = 0.0
        self.ang_mat = np.array([[math.cos(self.ang), -math.sin(self.ang)],
                                   [math.sin(self.ang), math.cos(self.ang)]])

        self.wheel_vel = 0.0
        self.wheel_ang = 0.0
        self.max_wheel_ang = math.pi/6

        self.points_mat = np.array([[self.pos[0] - self.size, self.pos[1] - self.size*2.5],
                                    [self.pos[0] + self.size, self.pos[1] - self.size*2.5],
                                    [self.pos[0] + self.size, self.pos[1] + self.size*2.5],
                                    [self.pos[0] - self.size, self.pos[1] + self.size*2.5]])
        
        self.wheel_pos = np.array([[-self.size,-self.size*1.6],
                                    [ self.size, -self.size*1.6],
                                    [ self.size, self.size*1.6],
                                    [-self.size, self.size*1.6],
                                    [0, self.size*1.6],
                                    [0, -self.size*1.6]])

        self.front_axel = np.array([self.pos[0], self.pos[1]  + self.size * 1.6])
        self.rear_axel = np.array([self.pos[0], self.pos[1]  - self.size * 1.6])

        self.wheels = []
        self.wheels.append(Wheel(window, colours["grey"], [self.pos[0] - self.size, self.pos[1] - self.size * 1.6], size / 3))
        self.wheels.append(Wheel(window, colours["grey"], [self.pos[0] + self.size, self.pos[1] - self.size * 1.6], size / 3))
        self.wheels.append(Wheel(window, colours["grey"], [self.pos[0] + self.size, self.pos[1] + self.size * 1.6], size / 3))
        self.wheels.append(Wheel(window, colours["grey"], [self.pos[0] - self.size, self.pos[1] + self.size * 1.6], size / 3))
            

    def dynamics(self, frame_time):
        pressed = pygame.key.get_pressed()

        #Rotation inputs
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

        #Limit rotation angle to maximum
        self.wheel_ang += self.wheel_vel * frame_time
        if self.wheel_ang > self.max_wheel_ang:
            self.wheel_ang = self.max_wheel_ang
        elif self.wheel_ang < -self.max_wheel_ang:
            self.wheel_ang = -self.max_wheel_ang

        
        #Translation inputs
        if pressed[pygame.K_w] and not pressed[pygame.K_s]:
            self.acc = 100
        elif not pressed[pygame.K_w] and pressed[pygame.K_s]:
            self.acc = -100
        else:
            if self.speed > 0.0001:
                self.acc = -50
            elif self.speed < 0.0001:
                self.acc = 50
            else:
                self.acc = 0

        #Limit speed to terminal speed
        if self.speed > self.term_speed:
            self.speed = self.term_speed
        elif self.speed < -self.term_speed:
            self.speed = -self.term_speed
            

        #Recalculate wheel positions
        wheel_pos = np.matmul(self.ang_mat, np.transpose(self.wheel_pos))
        wheel_pos = np.transpose(wheel_pos)

        #Find axel pivot points
        self.front_axel = wheel_pos[4]
        self.rear_axel = wheel_pos[5]

        #Recalculate wheel matrix
        self.front_mat = np.array([[math.cos(self.wheel_ang + self.ang), -math.sin(self.wheel_ang + self.ang)],
                                [math.sin(self.wheel_ang + self.ang), math.cos(self.wheel_ang + self.ang)]])
        
        #Calculate wheel normals
        self.front_norm = np.matmul(self.front_mat, np.transpose(np.array([1.0, 0.0])))
        self.front_norm = np.transpose(self.front_norm)
        self.rear_norm = np.matmul(self.ang_mat, np.transpose(np.array([1.0, 0.0])))
        self.rear_norm = np.transpose(self.rear_norm)

        #Find turing point
        mu = ((self.rear_norm[0]*(self.rear_axel[1] - self.front_axel[1]) - self.rear_norm[1]*(self.rear_axel[0] - self.front_axel[0]))
              / (self.rear_norm[0] * self.front_norm[1] - self.rear_norm[1] * self.front_norm[0]))
        turning_point = self.front_axel + mu * self.front_norm + self.pos

        #Move car geomery away from turning point
        self.points_mat = np.array([[self.points_mat[0][0] - turning_point[0], self.points_mat[0][1] - turning_point[1]],
                                    [self.points_mat[1][0] - turning_point[0], self.points_mat[1][1] - turning_point[1]],
                                    [self.points_mat[2][0] - turning_point[0], self.points_mat[2][1] - turning_point[1]],
                                    [self.points_mat[3][0] - turning_point[0], self.points_mat[3][1] - turning_point[1]]])
         
        
        #Calculate rotation angle
        radius = np.sqrt((self.pos - turning_point).dot(self.pos - turning_point))
        self.speed += self.acc * frame_time
        displacement = self.speed * frame_time
        angle = displacement / radius
        if self.wheel_ang < 0:
            angle *= -1
        self.ang += angle
        self.ang_mat = np.array([[math.cos(self.ang), -math.sin(self.ang)],
                                 [math.sin(self.ang), math.cos(self.ang)]])
        translation_mat = np.array([[math.cos(angle), -math.sin(angle)],
                                    [math.sin(angle), math.cos(angle)]])

        #Apply translation matrix
        self.points_mat = np.matmul(translation_mat, np.transpose(self.points_mat))
        self.points_mat = np.transpose(self.points_mat)

        #Move car geometry back from turning point
        self.points_mat = np.array([[self.points_mat[0][0] + turning_point[0], self.points_mat[0][1] + turning_point[1]],
                                    [self.points_mat[1][0] + turning_point[0], self.points_mat[1][1] + turning_point[1]],
                                    [self.points_mat[2][0] + turning_point[0], self.points_mat[2][1] + turning_point[1]],
                                    [self.points_mat[3][0] + turning_point[0], self.points_mat[3][1] + turning_point[1]]])


        self.pos = np.array([(self.points_mat[0][0] + self.points_mat[1][0] + self.points_mat[2][0] + self.points_mat[3][0]) / 4,
                             (self.points_mat[0][1] + self.points_mat[1][1] + self.points_mat[2][1] + self.points_mat[3][1]) / 4])

        #Recalculate wheel positions
        wheel_pos = np.matmul(self.ang_mat, np.transpose(self.wheel_pos))
        wheel_pos = np.transpose(wheel_pos)
        
        #Apply new wheel_positions
        self.wheels[0].set_pos([wheel_pos[0][0] + self.pos[0], wheel_pos[0][1] + self.pos[1]])
        self.wheels[1].set_pos([wheel_pos[1][0] + self.pos[0], wheel_pos[1][1] + self.pos[1]])
        self.wheels[2].set_pos([wheel_pos[2][0] + self.pos[0], wheel_pos[2][1] + self.pos[1]])
        self.wheels[3].set_pos([wheel_pos[3][0] + self.pos[0], wheel_pos[3][1] + self.pos[1]])

        #Apply new wheel rotations
        self.wheels[0].set_ang(self.ang)
        self.wheels[1].set_ang(self.ang)
        self.wheels[2].set_ang(self.wheel_ang + self.ang)
        self.wheels[3].set_ang(self.wheel_ang + self.ang)        

    def render(self):
        for wheel in self.wheels:
            wheel.render()
            
        pygame.draw.polygon(self.window, self.colours["red"], self.points_mat)

        
        
#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
