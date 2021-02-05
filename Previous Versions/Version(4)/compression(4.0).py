import pygame
import math
import numpy as np
import compression_o
import particles
import pygame_ui
from pygame.locals import *

def menu():
    pass


#----------------------------------------------------------------------------------------------------------------------------------
def simulation(window, clock, colours, resolution, phy_consts, action, mouse_used):
    border_inset = resolution[1]/36
    paused = False
    display_debug = False

    ball_pos = np.array([resolution[0]/2, resolution[1]/2])
    ball = compression_o.Compression_Ball(window, border_inset, ball_pos, phy_consts, 10, 100, 24, colours)

    while action == "compression_s":
        window.fill(colours["light_grey"])
        frame_time = clock.tick() / 1000

        #process inputs
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
                        
                elif event.key == pygame.K_x:
                    pass

                if event.key == K_p:
                    if paused:
                        paused = False
                    else:
                        paused = True

                if event.key == K_m:
                    action = "main"
                
                if event.key == K_ESCAPE:
                    pygame.quit()

        #Ball Processing
        ball.collisions(border_inset, resolution, phy_consts)
        ball.dynamics(frame_time)
        ball.render()

        particles.render_border(window, resolution, colours["grey"], border_inset)
        pygame.display.update()
        

    return action, mouse_used

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
