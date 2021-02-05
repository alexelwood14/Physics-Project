import pygame
import math
import numpy as np
from pygame.locals import *

class Ball_Node():
    def __init__(self, window, phy_consts, colour, pos):
        self.window = window
        self.colour = colour
        
        self.pos = pos
        self.vel = np.array([0.0,0.0])
        self.acc = np.array([0.0, phy_consts["g"]])

    def collisions(self, border_inset, resolution, phy_consts):
        if self.pos[1] >= resolution[1] - border_inset:
            self.acc = np.array([0.0, 0.0])
            self.pos[1] = resolution[1] - border_inset
        else:
            self.acc = np.array([0.0, phy_consts["g"]])

    def dynamics(self, frame_time):
        self.vel += self.acc * frame_time
        self.pos += self.vel * frame_time

    def render(self):
        pygame.draw.circle(self.window, self.colour, [int(self.pos[0]), int(self.pos[1])], int(5))

    def get_pos(self):
        return self.pos

class Ball_Spring():
    def __init__(self, window, colour, nat_len, node_1, node_2):
        self.window = window
        self.colour = colour

        self.nat_len = nat_len
        self.node_1 = node_1
        self.node_2 = node_2

    def render(self):
        pygame.draw.line(self.window, self.colour, self.node_1.get_pos(), self.node_2.get_pos(), 2)

class Compression_Ball():
    def __init__(self, window, border_inset, pos, phy_consts, mass, radius, node_count, colours):
        self.phy_consts = phy_consts
        self.window = window
        self.border_inset = border_inset
        self.colours = colours
        self.mass = mass

        #dynamics defaults
        self.pos = pos
        self.vel = np.array([0.0,0.0])
        self.acc = np.array([0.0,self.phy_consts["g"]])

        #Node setup
        self.nodes = []
        initial_pos = np.array([0, -radius])
        for node in range(node_count):
            angle = 2 * math.pi / node_count * node
            setup_mat = np.array([[math.cos(angle), -math.sin(angle)],
                                [math.sin(angle), math.cos(angle)]])
            node_pos = np.matmul(setup_mat, initial_pos)
            self.nodes.append(Ball_Node(window, phy_consts, colours["red"], self.pos + node_pos))

        #Spring setup
        self.springs = []
        for node in range(len(self.nodes)):
            if node != len(self.nodes) - 1:
                self.springs.append(Ball_Spring(window, colours["blue"], 5, self.nodes[node], self.nodes[node+1]))
            else:
                self.springs.append(Ball_Spring(window, colours["blue"], 5, self.nodes[node], self.nodes[0]))


    def collisions(self, border_inset, resolution, phy_consts):
        for node in self.nodes:
            node.collisions(border_inset, resolution, phy_consts)
            

    def dynamics(self, frame_time):
        for node in self.nodes:
            node.dynamics(frame_time)
            

    def render(self):
        #Render Nodes
        for node in self.nodes:
            node.render()

        #Render Springs
        for spring in self.springs:
            spring.render()

    #Setters and Getters
    def set_pos(self, pos):
        self.pos = np.array(pos)

    def get_pos(self):
        return self.pos

    def set_vel(self, vel):
        self.vel = np.array(vel)

    def get_vel(self):
        return self.vel

    def set_acc(self, acc):
        self.acc = np.array(acc)

    def get_mass(self):
        return self.mass

    def set_mass(self, mass):
        self.mass = mass


#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
