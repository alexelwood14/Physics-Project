import pygame
import math
import numpy as np
from pygame.locals import *

def find_angle(target_node, node_1, node_2):
    #Finds an angle using the cosine rule

    #Calculate triangle lengths
    a = np.sqrt((node_1 - node_2).dot(node_1 - node_2))
    b = np.sqrt((target_node - node_2).dot(target_node - node_2))
    c = np.sqrt((target_node - node_1).dot(target_node - node_1))
    
    if a == 0 or b == 0 or c == 0:
        return 0.0, b, c
    else:
        if (a**2 - b**2 - c**2) / (-2*b*c) > 1:
            return 0.0, b, c
        elif (a**2 - b**2 - c**2) / (-2*b*c) < -1:
            return math.pi, b, c
        else:
            return math.acos((a**2 - b**2 - c**2) / (-2*b*c)), b, c


class Ball_Node():
    def __init__(self, window, phy_consts, colour, pos, centre):
        self.window = window
        self.colour = colour
        
        self.pos = pos
        self.vel = np.array([0.0,0.0])
        self.acc = np.array([0.0, 0.0])

        self.cen_dist = np.sqrt((self.pos - centre).dot(self.pos - centre))

        vector = self.pos - centre
        self.bound_vec = vector / np.sqrt((vector).dot(vector))

        self.springs = []
        self.neighbors = []
            
        self.force = np.array([0.0, 0.0])


    def resolve_forces(self, gas_force, centre, area, resolution, border_inset, mass, phy_consts):
        #Reset Forces
        self.force = np.array([0.0, 0.0])

        #Apply Pressure Force
        self.cen_dist = np.sqrt((self.pos - centre).dot(self.pos - centre))
        self.force += gas_force * (self.pos - centre) / area 
        press_force = gas_force * (self.pos - centre) / area

        #Apply Skin Tension Forces
        for spring in self.springs:
            self.force +=  spring.get_force(self)

        #Apply Drag forces
        self.force -= self.vel * 30

        #Apply Gravitational Forces
        self.force[1] += phy_consts["g"] * mass

        #Apply Collision Forces
        if self.pos[1] >= resolution[1] - border_inset:
            self.pos[1] = resolution[1] - border_inset
            if self.force[1] > 0:
                self.force[1] = 0
        if self.pos[1] <= border_inset:
            self.pos[1] = border_inset
            if self.force[1] < 0:
                self.force[1] = 0
        if self.pos[0] >= resolution[0] - border_inset:
            self.pos[0] = resolution[0] - border_inset
            if self.force[0] > 0:
                self.force[0] = 0
        if self.pos[0] <= border_inset:
            self.pos[0] = border_inset
            if self.force[0] < 0:
                self.force[0] = 0


    def dynamics(self, frame_time, mass, centre):
        #Apply Dynamic Movements
        self.acc = self.force / mass
        self.vel += self.acc * frame_time
        self.pos += self.vel * frame_time

        #Move back to Bounding Vector
        self.mu = ((self.bound_vec[0] * (self.pos[0] - centre[0]) + self.bound_vec[1] * (self.pos[1] - centre[1])) /
              (self.bound_vec[0]**2 + self.bound_vec[1]**2))
        self.pos = np.array([centre[0] + self.mu * self.bound_vec[0], centre[1] + self.mu * self.bound_vec[1]])


    def render(self):
        pygame.draw.circle(self.window, self.colour, [int(self.pos[0]), int(self.pos[1])], int(5))
        
        
    def get_pos(self):
        return self.pos
    

    def add_spring(self, spring):
        self.springs.append(spring)
        

    def find_neighbors(self):
        for spring in self.springs:
            self.neighbors.append(spring.get_other_node(self))
            

    def get_cen_dist(self):
        return self.cen_dist

    
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
    

    def get_other_node(self, node):
        if self.node_1 == node:
            return self.node_2
        else:
            return self.node_1


#----------------------------------------------------------------------------------------------------------------------------------
class Compression_Ball():
    def __init__(self, window, border_inset, pos, phy_consts, mass, radius, node_count, colours):
        self.phy_consts = phy_consts
        self.window = window
        self.border_inset = border_inset
        self.colours = colours
        self.mass = mass
        self.radius = radius
        self.mod_elast = 1000
        self.gas_force = 2 * math.pi * radius**2 * self.mod_elast * math.cos((math.pi * (node_count - 2)) / 2 / node_count)
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
            self.nodes.append(Ball_Node(window, phy_consts, colours["red"], self.pos + node_pos, self.pos))

        #Spring setup
        self.springs = []
        for node in range(len(self.nodes)):
            if node != len(self.nodes) - 1:
                vector = self.nodes[node].get_pos() - self.nodes[node+1].get_pos()
                length = np.sqrt((vector).dot(vector))
                self.springs.append(Ball_Spring(window, colours["blue"], length / 2, self.mod_elast * 100, self.nodes[node], self.nodes[node+1]))
                self.nodes[node + 1].add_spring(self.springs[len(self.springs) - 1])
            else:
                vector = self.nodes[node].get_pos() - self.nodes[0].get_pos()
                length = np.sqrt((vector).dot(vector))
                self.springs.append(Ball_Spring(window, colours["blue"], length / 2, self.mod_elast * 100, self.nodes[node], self.nodes[0]))
                self.nodes[0].add_spring(self.springs[len(self.springs) - 1])

            self.nodes[node].add_spring(self.springs[len(self.springs) - 1])

        for node in self.nodes:
            node.find_neighbors()

        self.calc_area()


    def calc_area(self):
        #Calculate area
        self.area = 0.0
        for node in range(len(self.nodes) - 1):
            angle, b, c = find_angle(self.pos, self.nodes[node].get_pos(), self.nodes[node + 1].get_pos())
            self.area += (0.5 * b * c * math.sin(angle))


    def resolve_forces(self, resolution, border_inset):
        for node in self.nodes:
            node.resolve_forces(self.gas_force, self.pos, self.area, resolution, border_inset, self.mass, self.phy_consts)


    def dynamics(self, frame_time):
        average_pos = np.array([0.0, 0.0])
        for node in self.nodes:
            node.dynamics(frame_time, self.mass, self.pos)
            average_pos += node.get_pos()

        self.pos = average_pos / self.node_count

        self.calc_area()
        

    def render(self, wireframe):
        if wireframe:
            #Render Nodes
            for node in self.nodes:
                node.render()

            #Render Springs
            for spring in self.springs:
                spring.render()

        else:
            #Render Polygon
            node_points = []
            for node in self.nodes:
                node_points.append(node.get_pos())
            pygame.draw.polygon(self.window, self.colours["blue"], node_points)


#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
