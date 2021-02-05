import pygame
import math
import numpy as np
import objects
import pygame_ui
import random
from pygame.locals import *

def render_border(window, resolution, colour, border_inset):
    pygame.draw.rect(window, colour, [0, 0, resolution[0], border_inset])
    pygame.draw.rect(window, colour, [0, resolution[1] - border_inset, resolution[0], border_inset])
    pygame.draw.rect(window, colour, [0, 0, border_inset, resolution[1]])
    pygame.draw.rect(window, colour, [resolution[0] - border_inset, 0,  border_inset, resolution[1]])

def energy_check(dyn_objects, prev_energy, gravity, resolution):
    tolerance = 0.1
    energy = 0
    for obj in dyn_objects:
        #Add object kinetic energy
        speed = np.sqrt((dyn_objects[obj].get_vel()).dot(dyn_objects[obj].get_vel()))
        energy += 0.5 * dyn_objects[obj].get_mass() * (speed ** 2)
        #Add object gravitational energy
        energy += dyn_objects[obj].get_mass() * gravity * (resolution[1] - dyn_objects[obj].get_pos()[1])

    #Check for conservation violation
    if energy > prev_energy + prev_energy * tolerance:
        return True, energy
    else:
        return False, energy

def momentum_check(dyn_objects, prev_momentum):
    tolerance = 0.1
    momentum = [0, 0]
    for obj in dyn_objects:
        momentum[0] += dyn_objects[obj].get_mass() * dyn_objects[obj].get_vel()[0]
        momentum[1] += dyn_objects[obj].get_mass() * dyn_objects[obj].get_vel()[1]

    if (abs(momentum[0]) > abs(prev_momentum[0] + prev_momentum[0] * tolerance) or
        abs(momentum[1]) > abs(prev_momentum[1] + prev_momentum[1] * tolerance)):
        return True, momentum
    else:
        return False, momentum

def init_objects(window, resolution, border_inset, phy_consts, colours):

    dyn_objects = {}
    for i in range(5):
        dyn_objects["{}".format(i)] = objects.Sphere(window, border_inset, phy_consts, 10, 40, colours["yellow"])
##    sphere = objects.Sphere(window, border_inset, phy_consts, 10, 40, colours["yellow"])
##    sphere2 = objects.Sphere(window, border_inset, phy_consts, 10, 40, colours["light blue"])

    line_spacing = 70
    start_pos = [resolution[0]/1.2, resolution[1]/12]
    g_slider = objects.Slider(window, [start_pos[0], start_pos[1]], 1000, [colours["black"], colours["grey"], colours["white"]], 15, "Gravitational Acceleration")
    throw_slider = objects.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 4], 50, [colours["black"], colours["grey"], colours["white"]], 15, "Throw Strength")
    air_den_slider = objects.Slider(window, [start_pos[0], start_pos[1] + line_spacing], 0.02, [colours["black"], colours["grey"], colours["white"]], 15, "Air Density")
    co_rest_slider = objects.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 2], 1, [colours["black"], colours["grey"], colours["white"]], 15, "Coefficient of Restitution")
    co_fric_slider = objects.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 3], 0.5, [colours["black"], colours["grey"], colours["white"]], 15, "Coefficient of Friction")
##
##    dyn_objects = {"sphere" : sphere,
##                   "sphere2" : sphere2}

    quit_button = pygame_ui.Single_Button(window, [resolution[0] - 240, resolution[1] - 120],
                                          resolution[0]/6, "QUIT", colours["light_grey"], colours["grey"])

    start_button = pygame_ui.Single_Button(window, [resolution[0]/2, resolution[1]/2 + 240],
                                          resolution[0]/6, "START", colours["light_grey"], colours["grey"])
    
    sta_objects = {}
    sliders = {"g" : g_slider,
               "throw_strength" : throw_slider,
               "air_den" : air_den_slider,
               "co_rest" : co_rest_slider,
               "co_fric" : co_fric_slider}

    buttons = {"quit" : quit_button,
               "start" : start_button}

    return  dyn_objects, sta_objects, sliders, buttons

def simulation(window, clock, colours, resolution, border_inset, dyn_objects, sta_objects, sliders, phy_consts, action):
    mouse_down = False
    display_debug = False
    energy = 99999999999
    momentum = [0, 0]

    for i in dyn_objects:
        dyn_objects[i].set_pos([random.uniform(100,1820), random.uniform(100,980)])
        dyn_objects[i].set_vel([random.uniform(-1000,1000), random.uniform(-1000,1000)])
    
    while action == "sim":
        window.fill(colours["light_grey"])
        frame_time = clock.tick() / 1000
        
        #Input Processing
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

                if event.key == K_m:
                    action = "main"
                
                if event.key == K_ESCAPE:
                    pygame.quit()
                    
        #Call all main functions
        for obj in dyn_objects:
            dyn_objects[obj].dragged(mouse_down)
            dyn_objects[obj].collision(resolution, dyn_objects)
            dyn_objects[obj].dynamics(frame_time)
            dyn_objects[obj].render()

        for obj in sta_objects:
            sta_objects[obj].render()

        for slider in sliders:
            phy_consts[slider] = sliders[slider].dragging(mouse_down)
            sliders[slider].render()
            
        render_border(window, resolution, colours["grey"], border_inset)

        #Check for physics violations
        energy_violation, energy = energy_check(dyn_objects, energy, phy_consts["g"], resolution)
        momentum_violation, momentum = momentum_check(dyn_objects, momentum)

        #Display Debug Data
        if display_debug:
            line_spacing = resolution[1]/24
            text_size = int(resolution[0]/72)
            pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                      [resolution[0]/32, resolution[1]/14], text_size, colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "gravitational acceleration: {}".format(round(phy_consts["g"], 1)),
                      [resolution[0]/32, resolution[1]/14 + line_spacing], text_size, colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "air density: {}".format(round(phy_consts["air_den"], 3)),
                      [resolution[0]/32, resolution[1]/14 + line_spacing * 2], text_size, colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "coefficient of restitution: {}".format(round(phy_consts["co_rest"], 1)),
                      [resolution[0]/32, resolution[1]/14 + line_spacing * 3], text_size, colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "coefficient of friction: {}".format(round(phy_consts["co_fric"], 1)),
                      [resolution[0]/32, resolution[1]/14 + line_spacing * 4], text_size, colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "throw strength: {}".format(round(phy_consts["throw_strength"], 1)),
                      [resolution[0]/32, resolution[1]/14 + line_spacing * 5], text_size, colours["white"], "calibri", "ml")

            if not mouse_down:
                if energy_violation:
                    pygame_ui.draw_text(window, "ENERGY CONSERVATION VIOLATION",
                      [resolution[0]/32, resolution[1]/14 + line_spacing * 6], text_size, colours["red"], "calibri", "ml")
                if momentum_violation:
                    pygame_ui.draw_text(window, "MOMENTUM CONSERVATION VIOLATION",
                      [resolution[0]/32, resolution[1]/14 + line_spacing * 7], text_size, colours["red"], "calibri", "ml")
            
            for obj in dyn_objects:
                dyn_objects[obj].force_lines(colours)

        pygame.display.update()

    return action

def main_menu(colours, window, resolution, border_inset, action, buttons):
    while action == "main":
        
        window.fill(colours["light_grey"])
        pygame.draw.lines(window, colours["grey"], True, ((0,0), (resolution[0],0),
                                                         (resolution[0],resolution[1]), (0,resolution[1])), 20)
        pygame_ui.draw_text(window, 'PHYSICS SIMULATOR', [int(resolution[0] / 2),
                           int(resolution[1] / 10)], int(resolution[1] / 10.5), colours["grey"], 'calibri', 'c')

        #Process single buttons
        if buttons["quit"].highlight():
            pygame.quit()
            quit()

        if buttons["start"].highlight():
            action = "sim"

        #Render single buttons
        for button in buttons:
            buttons[button].render()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

        
        pygame.display.update()

    return action

def main():
    phy_consts = {"g" : 500.0,
                  "air_den" : 0.01,
                  "co_rest" : 0.85,
                  "co_fric" : 0.1,
                  "throw_strength" : 50}

    colours = {"white" : [255,255,255],
               "red" : [255,0,0],
               "blue" : [0,0,255],
               "light blue" : [0, 255, 255],
               "green" : [0, 255, 0],
               "yellow" : [255,255,0],
               "black" : [0,0,0],
               "grey" : [70, 70, 70],
               "light_grey" : [150, 150, 150]}

    clock = pygame.time.Clock()
    resolution = [1920, 1080]
    border_inset = 30
    pygame.init()
    window = pygame.display.set_mode((resolution[0], resolution[1]))
    pygame.display.set_caption('Physics')

    dyn_objects, sta_objects, sliders, buttons = init_objects(window, resolution, border_inset, phy_consts, colours)

    action = "main"
    while True:
        if action == "main":
            action = main_menu(colours, window, resolution, border_inset, action, buttons)
        elif action == "sim":
            action = simulation(window, clock, colours, resolution, border_inset, dyn_objects, sta_objects, sliders, phy_consts, action)
        
            
if __name__ == "__main__":
    main()
