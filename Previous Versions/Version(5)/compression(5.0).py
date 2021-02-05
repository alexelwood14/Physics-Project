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
    text_size = int(resolution[0]/72)
    border_inset = resolution[1]/36
    paused = False
    display_debug = False
    wireframe = False

    ball_pos = np.array([resolution[0]/2, resolution[1]/2])
    ball = compression_o.Compression_Ball(window, border_inset, ball_pos, phy_consts, 10, 300, 100, colours)

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
                    if wireframe:
                        wireframe = False
                    else:
                        wireframe = True

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
        if not paused:
            ball.resolve_forces(resolution, border_inset)
            ball.dynamics(frame_time)
        ball.render(wireframe)

        if display_debug:
            pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                      [resolution[0]/32, resolution[1]/14], text_size, colours["white"], "calibri", "ml")


        particles.render_border(window, resolution, colours["grey"], border_inset)
        pygame.display.update()
        

    return action, mouse_used

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
