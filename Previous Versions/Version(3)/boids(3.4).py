import pygame
import math
import numpy as np
import pygame_ui
import boids_o
import random
from pygame.locals import *

def simulation(colours, clock, window, resolution, border_inset, action, buttons, mouse_used):
    display_debug = False
    #generate boids
    boids = []
    boid_size = 10
    vision_range = 200
    for i in range(100):
        boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range))

    while action == "boids_s":
        #Process inputs
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
           
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if display_debug:
                        display_debug = False
                    else:
                        display_debug = True

            if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        quit()

        window.fill(colours["light_grey"])
        frame_time = clock.tick() / 1000

        #render boids
        for boid in boids:
            boid.visible_boids(boids, colours)
            boid.calc_ang_vel()
            boid.dynamics(frame_time, resolution)
            if display_debug:
                boid.render(colours, True)
            else:
                boid.render(colours)

        pygame.draw.lines(window, colours["grey"], True, ((0,0), (resolution[0],0),
                                                         (resolution[0],resolution[1]), (0,resolution[1])), int(resolution[1]/54))
        pygame.display.update()

    return action, mouse_used

def menu():
    pass

def main():
    pass

if __name__ == "__main__":
    main()
