import pygame
import math
import numpy as np
import pygame_ui
import boids_o
import random
from pygame.locals import *

def simulation(colours, clock, window, resolution, border_inset, action, buttons, mouse_used):
    #generate boids
    boids = []
    boid_size = 20
    vision_range = 200
##    for i in range(5):
##        boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range))
    boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range, [290.0,210.0],1))
    boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range, [250.0,250.0],1))

    boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range, [210.0,460.0],1))
    boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range, [250.0,500.0],1))
##
##    boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range, [1290.0,210.0]))
##    boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range, [1250.0,250.0]))
##
##    boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range, [1210.0,460.0]))
##    boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range, [1250.0,500.0]))
    
    while action == "boids_s":
        #Reset mouse usage
        if not pygame.mouse.get_pressed()[0]:
            mouse_used = False

        window.fill(colours["light_grey"])
        frame_time = clock.tick() / 1000

        boids[0].visible_boids(boids, colours)
        boids[1].visible_boids(boids, colours)
        boids[2].visible_boids(boids, colours)
        boids[3].visible_boids(boids, colours)


        #render boids
        for boid in boids:
            boid.dynamics(frame_time, resolution)
            boid.render_arc(colours, vision_range)
            boid.render()
        
        for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        quit()

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
