import pygame
import math
import numpy as np
import turning_o
import particles
import pygame_ui
from pygame.locals import *

def menu():
    pass


#----------------------------------------------------------------------------------------------------------------------------------
def simulation(window, clock, colours, resolution, phy_consts, action, mouse_used):
    text_size = int(resolution[0]/72)
    border_inset = resolution[1]/36
    paused = False
    display_debug = False

    car = turning_o.Car(window, colours, [resolution[0]/2, resolution[1]/2], 30)

    while action == "turning_s":
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

                if event.key == K_p:
                    if paused:
                        paused = False
                    else:
                        paused = True

                if event.key == K_m:
                    action = "main"
                
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()


        #Car Processing
        car.dynamics(frame_time)
        car.render()

        if display_debug:
            pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                      [resolution[0]/32, resolution[1]/14], text_size, colours["white"], "calibri", "ml")
            car.display_debug()


        particles.render_border(window, resolution, colours["grey"], border_inset)
        pygame.display.update()
        

    return action, mouse_used

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
