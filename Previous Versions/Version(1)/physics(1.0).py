import pygame
import math
import numpy as np
import objects
from pygame.locals import *

def init_objects(window, resolution, g, air_den, colours):
    square = objects.Square(window, g, air_den, 2, 30, colours["red"])

    thickness = 20
    top_border = objects.Border(window, [resolution[0], thickness], colours["grey"])
    bottom_border = objects.Border(window, [resolution[0], thickness], colours["grey"])
    left_border = objects.Border(window, [thickness, resolution[1]], colours["grey"])
    right_border = objects.Border(window, [thickness, resolution[1]], colours["grey"])

    dyn_objects = {"square" : square}
    sta_objects = {"top_border" : top_border,
                   "bottom_border" : bottom_border,
                   "left_border" : left_border,
                   "right_border" : right_border}

    return  dyn_objects, sta_objects

def simulation(window, clock, colours, resolution, dyn_objects, sta_objects):
    border_inset = 10
    sta_objects["top_border"].set_pos([resolution[0]/2, border_inset])
    sta_objects["bottom_border"].set_pos([resolution[0]/2, resolution[1]-border_inset])
    sta_objects["left_border"].set_pos([border_inset, resolution[1]/2])
    sta_objects["right_border"].set_pos([resolution[0] - border_inset, resolution[1]/2])

    dyn_objects["square"].set_pos([resolution[0]/2, resolution[1]/2])
    dyn_objects["square"].set_vel([200.0, 2000.0])
    
    while True:
        window.fill(colours["light_grey"])
        frame_time = clock.tick() / 1000
        for obj in dyn_objects:
            dyn_objects[obj].collision(resolution)
            dyn_objects[obj].dynamics(frame_time)
            dyn_objects[obj].render()

        for obj in sta_objects:
            sta_objects[obj].render()

        pygame.display.update()

def main():
    g = 500
    air_den = 0.0015

    white = [255,255,255]
    red = [255,0,0]
    grey = [70, 70, 70]
    light_grey = [150, 150, 150]
    colours = {"white" : white,
               "red" : red,
               "grey" : grey,
               "light_grey" : light_grey}

    clock = pygame.time.Clock()
    resolution = [1920, 1080]
    pygame.init()
    window = pygame.display.set_mode((resolution[0], resolution[1]))
    pygame.display.set_caption('Physics')

    dyn_objects, sta_objects = init_objects(window, resolution, g, air_den, colours)

    while True:
        simulation(window, clock, colours, resolution, dyn_objects, sta_objects)
        
            
if __name__ == "__main__":
    main()
