import pygame
import math
import numpy as np
import pygame_ui
import boids_o
import random
from pygame.locals import *

def calc_grid(boids, size):
    grid = []
    for i in range(size[0]):
        grid.append([])
        for j in range(size[1]):
            grid[i].append([])

    for boid in boids:
        coords = boid.get_grid_coords()
        grid[coords[0]][coords[1]].append(boid)
        
    return grid

def simulation(colours, clock, window, resolution, border_inset, action, buttons, mouse_used):
    display_debug = False
    heatmap = False
    pause = False
    display_data = False
    
    #generate boids
    boids = []
    boid_size = 8
    number =  60
    vision_range = 100
    grid_size = [resolution[0] // vision_range + 1, resolution[1] // vision_range + 1]
    for i in range(30):
        boids.append(boids_o.boid(window, colours["red"], boid_size, resolution, vision_range))
    for i in range(30):
        boids.append(boids_o.boid(window, colours["blue"], boid_size, resolution, vision_range))
    for i in range(30):
        boids.append(boids_o.boid(window, colours["green"], boid_size, resolution, vision_range))

        
    grid = calc_grid(boids, grid_size)

    while action == "boids_s":
        #Process inputs
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
           
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    if display_debug:
                        display_debug = False
                    else:
                        display_debug = True

                if event.key == pygame.K_c:
                    if heatmap:
                        heatmap = False
                    else:
                        heatmap = True

                if event.key == pygame.K_p:
                    if pause:
                        pause = False
                    else:
                        pause = True

                if event.key == pygame.K_z:
                    if display_data:
                        display_data = False
                    else:
                        display_data = True

                if event.key == pygame.K_m:
                    action = "main"

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()

        window.fill(colours["light_grey"])
        frame_time = clock.tick() / 1000

        #Display heatmap
        if heatmap:
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    x = len(grid[i][j])/(number/7)
                    if x > 1:
                        x = 1
                    colour = (150 + 105*x, 150 - 150*x, 150 - 150*x)
                    pygame.draw.rect(window, colour, [vision_range * i, vision_range * j, vision_range, vision_range])

        if display_data:
            text_size = int(resolution[0]/72)
            pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                      [resolution[0]/32, resolution[1]/14], text_size, colours["white"], "calibri", "ml")

        #calc boid movement
        for boid in boids:
            boid.visible_boids(boids, grid)
            boid.calc_ang_vel()
            boid.calc_wall_avoid(resolution)

        #render boids
        for boid in boids:
##            boid.visible_boids(boids, grid)
            if not pause:
                boid.dynamics(frame_time, resolution)
            if display_debug:
                boid.render(colours, True)
            else:
                boid.render(colours)

        grid = calc_grid(boids, grid_size)

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
