import pygame
import math
import numpy as np
import statistics as stat
from pygame.locals import *

def draw_text(window, text, size, pos, colour):
    font = pygame.font.Font(pygame.font.match_font("Ariel"), size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    text_rect.center = (pos[0], pos[1])
    window.blit(text_surface, text_rect)

class Slider():
    def __init__(self, window, pos, maximum, colours, size, name):
        self.window = window
        self.name = name
        self.maximum = maximum
        self.size = size
        self.colours = colours
        self.pos = pos
        self.slider_pos = 50.0
        self.grabbed = False

    def dragging(self, mouse_down):
        if mouse_down:
            mouse_pos = pygame.mouse.get_pos()
            slider_pos = self.pos[0] + self.size * 12 * self.slider_pos / 100
            if (mouse_pos[0] <= slider_pos + self.size and mouse_pos[0] >= slider_pos and
                mouse_pos[1] <= self.pos[1] + self.size and mouse_pos[1] >= self.pos[1] - self.size) or self.grabbed:

                self.grabbed = True

                self.slider_pos = (mouse_pos[0] - self.size/2 - self.pos[0]) / self.size / 12 * 100
                if self.slider_pos > 100:
                    self.slider_pos = 100
                elif self.slider_pos < 0:
                    self.slider_pos = 0
                    
            else:
                self.grabbed = False
        else:
            self.grabbed = False

        return float(self.maximum * self.slider_pos / 100)

    def render(self):
        pygame.draw.rect(self.window, self.colours[0], [self.pos[0], self.pos[1] - self.size/2, self.size * 13, self.size])
        pygame.draw.rect(self.window, self.colours[1], [self.pos[0] + self.size * 14, self.pos[1] - self.size * 1.25, self.size * 4, self.size * 2.5])
        draw_text(self.window, self.name, self.size * 2, [self.pos[0] + self.size * 9, self.pos[1] - self.size * 2.2], self.colours[2])
        draw_text(self.window, "{}%".format(str(int(self.slider_pos))), self.size * 2, [self.pos[0] + self.size * 16, self.pos[1], self.size * 4, self.size * 2.5], self.colours[2])

        pygame.draw.rect(self.window, self.colours[1], [self.pos[0] + self.size * 12 * self.slider_pos / 100, self.pos[1] - self.size, self.size, self.size * 2])

#Parent Classes
class Dynamic_object():
    def __init__(self, window, border_inset, phy_consts, mass, colour):
        self.phy_consts = phy_consts
        self.window = window
        self.border_inset = border_inset
        self.pos = np.array([0.0,0.0])
        self.vel = np.array([0.0,0.0])
        self.acc = np.array([0.0,self.phy_consts["g"]])
        self.mass = mass
        self.grabbed = False
        self.on_ground = False
        self.ground_col = False
        self.movements = []
        self.colour = colour

    def dynamics(self, frame_time):
        if not self.grabbed:
            self.drag = (self.vel ** 2) * self.phy_consts["air_den"] / float(self.mass)
            
            if self.vel[0] > 0:
                self.drag[0] *= -1
            if self.vel[1] > 0:
                self.drag[1] *= -1

            self.acc = np.array([self.drag[0],self.drag[1]])        
            if not self.on_ground:
                self.acc[1] += self.phy_consts["g"]
                self.vel += self.acc * frame_time
                self.fric = 0.0
                
            else:
                if self.vel[0] >= 0:
                    self.fric = -self.phy_consts["co_fric"] * self.phy_consts["g"]
                else:
                    self.fric = self.phy_consts["co_fric"] * self.phy_consts["g"]
                self.acc[0] += self.fric
                self.vel[0] += self.acc[0] * frame_time
                self.vel[1] = 0.0

            self.pos += self.vel * frame_time

    def dragging(self, mouse_pos):
        self.grabbed = True
        self.on_ground = False
        prev_pos = self.pos
        self.pos = np.array([float(mouse_pos[0]), float(mouse_pos[1])])

        self.movements.append(self.pos - prev_pos)
        while len(self.movements) >= 10:
            self.movements.pop(0)

        vel = np.array([0.0,0.0])
        for move in self.movements:
            vel += move
        vel *= self.phy_consts["throw_strength"]
        
        self.vel = vel
        self.acc = np.array([0.0,0.0])

    def border_collision(self, size, resolution):
        if self.pos[1] >= resolution[1] - size - self.border_inset:
            if self.ground_col:
                self.on_ground = True
            else:
                self.on_ground = False
                self.pos[1] = resolution[1] - size - self.border_inset
                self.vel[1] = -self.vel[1] * self.phy_consts["co_rest"]
                self.ground_col = True

        elif self.pos[1] <= size + self.border_inset:
            self.pos[1] = size + self.border_inset
            self.vel[1] = -self.vel[1] * self.phy_consts["co_rest"]
            self.ground_col = False
        else:
            self.ground_col = False


        if self.pos[0] >= resolution[0] - size - self.border_inset:
            self.pos[0] = resolution[0] - size - self.border_inset
            self.vel[0] = -self.vel[0] * self.phy_consts["co_rest"]

        elif self.pos[0] <= size + self.border_inset:
            self.pos[0] = size + self.border_inset
            self.vel[0] = -self.vel[0] * self.phy_consts["co_rest"]

    def force_lines(self, colours):
        pygame.draw.line(self.window, colours["red"], self.pos, self.pos + self.drag / 3, 3)
        pygame.draw.line(self.window, colours["blue"], self.pos, [self.pos[0], self.pos[1] + self.phy_consts["g"] / 3], 3)
        if abs(self.vel[0]) > 8:
            pygame.draw.line(self.window, colours["yellow"], self.pos, [self.pos[0] + self.fric / 3, self.pos[1]], 3)
        if self.on_ground or self.ground_col:
            pygame.draw.line(self.window, colours["green"], self.pos, [self.pos[0], self.pos[1] - self.phy_consts["g"] / 3], 3)

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

    def set_phy_consts(self, phy_consts):
        self.phy_consts = phy_consts
    

class Static_object():
    def __init__(self, window, colour):
        self.window = window
        self.pos = np.array([0,0])
        self.colour = colour

    def set_pos(self, pos):
        self.pos = np.array(pos)

#Subclasses
class Square(Dynamic_object):
    def __init__(self, window, border_inset, phy_consts, mass, size, colour):
        super().__init__(window, border_inset, phy_consts, mass, colour)
        self.size = size

    def collision(self, resolution, dyn_objects):
        if not self.grabbed:
            self.border_collision(self.size/2, resolution)

    def dragged(self, mouse_down):
        if mouse_down:
            mouse_pos = pygame.mouse.get_pos()
            if (mouse_pos[0] <= self.pos[0] + self.size/2 and mouse_pos[0] >= self.pos[0] - self.size/2 and
                mouse_pos[1] <= self.pos[1] + self.size/2 and mouse_pos[1] >= self.pos[1] - self.size/2) or self.grabbed:
                
                self.dragging(mouse_pos)

            else:
                self.movements = []
                self.grabbed = False
        else:
            self.movements = []
            self.grabbed = False
            

    def render(self):
        pygame.draw.rect(self.window, self.colour, [self.pos[0] - self.size/2, self.pos[1] - self.size/2, self.size, self.size])

class Sphere(Dynamic_object):
    def __init__(self, window, border_inset, phy_consts, mass, radius, colour):
        super().__init__(window, border_inset, phy_consts, mass, colour)
        self.radius = radius

    def collision(self, resolution, dyn_objects):

        sphere_collision = False
        #Collision with sphere
        for obj in dyn_objects:
            if dyn_objects[obj] != self and dyn_objects[obj].__class__.__name__ == "Sphere":
                los_vec = np.array(dyn_objects[obj].get_pos() - self.pos)
                distance = np.sqrt((los_vec).dot(los_vec))
                
                if distance <= self.radius + dyn_objects[obj].get_radius():
                    
                    #Calculate the local axis
                    local_x = los_vec / math.sqrt(los_vec[0] ** 2 + los_vec[1] ** 2)
                    local_y = np.array([-local_x[1], local_x[0]])

                    #Reposition to remove overlap
                    overlap = self.radius + dyn_objects[obj].get_radius() - distance
                    self.pos = self.pos - overlap * local_x

                    #Convert local velocity to the local referance frame
                    local_u = np.array([np.dot(self.vel, local_x), np.dot(self.vel, local_y)])
                    target_vel = dyn_objects[obj].get_vel()
                    target_local_u = np.array([np.dot(target_vel, local_x), np.dot(target_vel, local_y)])

                    #Calculate the local velocity after collision
                    target_mass = dyn_objects[obj].get_mass()
                    local_v = np.array([0.0,0.0])
                    local_v[0] = (((self.phy_consts["co_rest"]) * target_mass * target_local_u[0] +
                                  (self.mass - self.phy_consts["co_rest"] * target_mass) * local_u[0]) /
                                  (target_mass + self.mass))
                    local_v[1] = local_u[1]

                    #Convert local velocity to the global referance frame
                    self.vel[0] = np.dot(local_v, np.array([1,0]))
                    self.vel[1] = np.dot(local_v, np.array([0,1]))

                    sphere_collision = True

        #Collision with border
        if not self.grabbed and not sphere_collision:
            self.border_collision(self.radius, resolution)

    def dragged(self, mouse_down):
        if mouse_down:
            mouse_pos = np.array(pygame.mouse.get_pos())
            if np.sqrt((mouse_pos - self.pos).dot(mouse_pos - self.pos)) <= self.radius or self.grabbed:

                self.dragging(mouse_pos)

            else:
                self.movements = []
                self.grabbed = False
        else:
            self.movements = []
            self.grabbed = False

    def render(self):
        pygame.draw.circle(self.window, self.colour, [int(self.pos[0]), int(self.pos[1])], self.radius)

    def get_radius(self):
        return self.radius
