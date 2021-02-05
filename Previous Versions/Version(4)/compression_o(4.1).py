import pygame
import math
import numpy as np
from pygame.locals import *

class Ball_Node():
    def __init__(self, window, phy_consts, colour, pos, debug):
        self.window = window
        self.colour = colour
        
        self.pos = pos
        self.vel = np.array([0.0,0.0])
        self.acc = np.array([0.0, 0.0])

        self.springs = []
        self.force = np.array([0.0, 0.0])

        self.debug = debug


    def resolve_forces(self, pressure, centre, area):
        self.force = np.array([0.0, 0.0])
        dist_from_centre = np.sqrt((self.pos - centre).dot(self.pos - centre))
        self.force += pressure * (self.pos - centre) / area / dist_from_centre
        press_force = pressure * (self.pos - centre) / area / dist_from_centre
        for spring in self.springs:
            self.force +=  spring.get_force(self)

        if self.col:
            self.force[1] = 0

        if self.debug:
            print("press:  {}".format(press_force[1]))
            print("all   : {}".format(self.force[1]))

        

    def collisions(self, border_inset, resolution, phy_consts):
        if self.pos[1] >= resolution[1] - border_inset:
            self.col = True
            self.pos[1] = resolution[1] - border_inset
        else:
            self.col = False
            

    def dynamics(self, frame_time, mass, phy_consts):
        self.acc = self.force / mass
##        self.acc[1] += phy_consts["g"]
##        self.acc += np.array([0.0, 50.0])
        self.vel += self.acc * frame_time
        if self.col:
            self.vel[1] = 0.0
        self.pos += self.vel * frame_time


    def render(self):
        pygame.draw.circle(self.window, self.colour, [int(self.pos[0]), int(self.pos[1])], int(5))
        

    def get_pos(self):
        return self.pos

    def add_spring(self, spring):
        self.springs.append(spring)

    
#----------------------------------------------------------------------------------------------------------------------------------
class Ball_Spring():
    def __init__(self, window, colour, nat_len, mod_elast, node_1, node_2):
        self.window = window
        self.colour = colour

        self.nat_len = nat_len
        self.mod_elast = mod_elast
        self.node_1 = node_1
        self.node_2 = node_2
        

    def render(self):
        pygame.draw.line(self.window, self.colour, self.node_1.get_pos(), self.node_2.get_pos(), 2)

    def get_force(self, node):
        vector = self.node_1.get_pos() - self.node_2.get_pos()
        length = np.sqrt((vector).dot(vector))
        extension = length - self.nat_len
        abs_force = self.mod_elast * extension / self.nat_len

        if node == self.node_2:
            force = vector / length * abs_force
        elif node == self.node_1:
            force = vector / length * abs_force * -1
        
        return force


#----------------------------------------------------------------------------------------------------------------------------------
class Compression_Ball():
    def __init__(self, window, border_inset, pos, phy_consts, mass, radius, node_count, colours):
        self.phy_consts = phy_consts
        self.window = window
        self.border_inset = border_inset
        self.colours = colours
        self.mass = mass
        self.node_count = node_count

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
            if node == 0:
                self.nodes.append(Ball_Node(window, phy_consts, colours["red"], self.pos + node_pos, True))
            else:
                self.nodes.append(Ball_Node(window, phy_consts, colours["red"], self.pos + node_pos, False))

        #Spring setup
        self.springs = []
        for node in range(len(self.nodes)):
            if node != len(self.nodes) - 1:
                vector = self.nodes[node].get_pos() - self.nodes[node+1].get_pos()
                length = np.sqrt((vector).dot(vector))
                self.springs.append(Ball_Spring(window, colours["blue"], length, length * 100, self.nodes[node], self.nodes[node+1]))
                self.nodes[node + 1].add_spring(self.springs[len(self.springs) - 1])
            else:
                vector = self.nodes[node].get_pos() - self.nodes[0].get_pos()
                length = np.sqrt((vector).dot(vector))
                self.springs.append(Ball_Spring(window, colours["blue"], length, length * 100, self.nodes[node], self.nodes[0]))
                self.nodes[0].add_spring(self.springs[len(self.springs) - 1])

            self.nodes[node].add_spring(self.springs[len(self.springs) - 1])

        self.calc_area()


    def calc_area(self):
        #Calculate area
        self.area = 0.0
        for node in range(len(self.nodes) - 1):
            node_1 = self.nodes[node].get_pos()
            node_2 = self.nodes[node + 1].get_pos()
            a = np.sqrt((node_1 - node_2).dot(node_1 - node_2))
            b = np.sqrt((self.pos - node_2).dot(self.pos - node_2))
            c = np.sqrt((self.pos - node_1).dot(self.pos - node_1))
            if a == 0 or b == 0 or c == 0:
                pass
            else:
                angle = math.acos((a**2 - b**2 - c**2) / (-2*b*c))
                self.area += (0.5 * b * c * math.sin(angle))


    def resolve_forces(self):
        for node in self.nodes:
            node.resolve_forces(100000, self.pos, self.area)


    def collisions(self, border_inset, resolution, phy_consts):
        for node in self.nodes:
            node.collisions(border_inset, resolution, phy_consts)
            

    def dynamics(self, frame_time):
        average_pos = np.array([0.0, 0.0])
        for node in self.nodes:
            node.dynamics(frame_time, self.mass, self.phy_consts)
            average_pos += node.get_pos()

        self.pos = average_pos / self.node_count

        self.calc_area()
        

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
