import pygame
import math
import numpy as np
import particles
import boids
import pygame_ui
import random
from pygame.locals import *

#----------------------------------------------------------------------------------------------------------------------------------
def init_objects(window, resolution, border_inset, phy_consts, colours):
    
    #initiate sliders
    line_spacing = resolution[1] * 7 / 108
    start_pos = [resolution[0]/1.2, resolution[1]/12]
    g_slider = pygame_ui.Slider(window, [start_pos[0], start_pos[1]], resolution[0] * 48/25, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Gravitational Acceleration")
    throw_slider = pygame_ui.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 4], 50, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Throw Strength")
    air_den_slider = pygame_ui.Slider(window, [start_pos[0], start_pos[1] + line_spacing], 0.02, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Air Density")
    co_rest_slider = pygame_ui.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 2], 1, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Coefficient of Restitution")
    co_fric_slider = pygame_ui.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 3], 0.5, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Coefficient of Friction")

    #initiate text buttons
    start = resolution[1] * 41 / 108
    incriment = resolution[1] * 7 / 54
    quit_button = pygame_ui.Single_Button(window, [resolution[1] / 3.6, start + incriment * 4],
                                          resolution[0]/5, resolution[0] / 30, "QUIT", colours["light_grey"], colours["grey"])

    initiate_button = pygame_ui.Single_Button(window, [resolution[1] / 3.6, start + incriment * 2],
                                          resolution[0]/5, resolution[0] / 30, "INITIATE", colours["light_grey"], colours["grey"])

    back_button = pygame_ui.Single_Button(window, [resolution[0]/2, resolution[1] - resolution[0] / 16],
                                          resolution[0]/5, resolution[0] / 30, "BACK", colours["light_grey"], colours["grey"])

    apply_button = pygame_ui.Single_Button(window, [resolution[0]/2, resolution[1] - resolution[0] / 7.5],
                                          resolution[0]/5, resolution[0] / 30, "APPLY", colours["light_grey"], colours["grey"])

    rand_all_button = pygame_ui.Single_Button(window, [resolution[1] / 3.6, start + incriment],
                                          resolution[0]/5, resolution[1] * 5 / 108, "RANDOMISE ALL", colours["light_grey"], colours["grey"])

    uniform_button = pygame_ui.Single_Button(window, [resolution[1] / 3.6, start],
                                          resolution[0]/5, resolution[1] * 5 / 108, "UNIFORM PRESET", colours["light_grey"], colours["grey"])

    settings_button = pygame_ui.Single_Button(window, [resolution[1] / 3.6, start + incriment * 3],
                                          resolution[0]/5, resolution[0] / 30, "SETTINGS", colours["light_grey"], colours["grey"])

    rand_colour_button = pygame_ui.Single_Button(window, [resolution[1] / 1.35, resolution[1] - resolution[1] / 10.8],
                                          resolution[0]/8, resolution[1] / 27, "RANDOMISE", colours["light_grey"], colours["grey"])

    rand_radius_button = pygame_ui.Single_Button(window, [resolution[1] / 0.9, resolution[1] - resolution[1] / 10.8],
                                          resolution[0]/8, resolution[1] / 27, "RANDOMISE", colours["light_grey"], colours["grey"])

    rand_mass_button = pygame_ui.Single_Button(window, [resolution[0] / 1.2, resolution[1] - resolution[1] / 10.8],
                                          resolution[0]/8, resolution[1] / 27, "RANDOMISE", colours["light_grey"], colours["grey"])

    #Initiate Ball Creators
    add_creator = pygame_ui.Add_Creator(window, [resolution[0] /1.55, resolution[1] / 13.5] , colours)

    #Initiate Scroll Bar
    scroll_bar = pygame_ui.Scroll_Bar(window, [resolution[0] - resolution[0] * 3 / 128, resolution[1] / 2], colours["grey"], resolution)

    #Initiate Arrows
    res_up   = pygame_ui.Up_Arrow(  window, [resolution[0]/2 - resolution[0]/7, resolution[1]/3], resolution[1]/54, colours["grey"], colours["light_grey"])
    res_down = pygame_ui.Down_Arrow(window, [resolution[0]/2 - resolution[0]/7, resolution[1]/3], resolution[1]/54, colours["grey"], colours["light_grey"])
    screen_up   = pygame_ui.Up_Arrow(  window, [resolution[0]/2 - resolution[0]/7, resolution[1]/2], resolution[1]/54, colours["grey"], colours["light_grey"])
    screen_down = pygame_ui.Down_Arrow(window, [resolution[0]/2 - resolution[0]/7, resolution[1]/2], resolution[1]/54, colours["grey"], colours["light_grey"])

    #Image Buttons
    boids_button = pygame_ui.Image_Button(window, [resolution[0]/2 - resolution[0]/8, resolution[1]/3], (int(resolution[0]/6), int(resolution[1]/6)), "BOIDS SIMULATION", 28, "boids_sim", colours)
    particles_button = pygame_ui.Image_Button(window, [resolution[0]/2 + resolution[0]/8, resolution[1]/3], (int(resolution[0]/6), int(resolution[1]/6)), "PARTICLE SIMULATION", 28, "particle_sim", colours)
    

    #Add all objects to dictionarys
    sta_objects = {}
    sliders = {"g" : g_slider,
               "throw_strength" : throw_slider,
               "air_den" : air_den_slider,
               "co_rest" : co_rest_slider,
               "co_fric" : co_fric_slider}

    buttons = {"quit" : quit_button,
               "initiate" : initiate_button,
               "back" : back_button,
               "apply" : apply_button,
               "rand_all" : rand_all_button,
               "rand_colour" : rand_colour_button,
               "rand_radius" : rand_radius_button,
               "rand_mass" : rand_mass_button,
               "settings" : settings_button,
               "uniform" : uniform_button,
               "add_creator" : add_creator,
               "scroll_bar" : scroll_bar,
               "res_up" : res_up,
               "res_down" : res_down,
               "screen_up" : screen_up,
               "screen_down" : screen_down,
               "boids" : boids_button,
               "particles" : particles_button
               }          

    return  sta_objects, sliders, buttons

#--------------------------------------------------------------------------------------------------------------
def settings(colours, window, resolution, border_inset, action, buttons, mouse_used):
    resolutions = [[1280,720],
                   [1920,1080],
                   [2560,1440]]
    res = 0
    fullscreen = False

    used_buttons = {"back" : buttons["back"],
                    "apply" : buttons["apply"],
                    "res_up" : buttons["res_up"],
                    "res_down" : buttons["res_down"],
                    "screen_up" : buttons["screen_up"],
                    "screen_down" : buttons["screen_down"]}
    
    while action == "settings":
        #Reset mouse usage
        if not pygame.mouse.get_pressed()[0]:
            mouse_used = False

        #render user interface elements
        window.fill(colours["light_grey"])
        pygame_ui.draw_text(window, 'SETTINGS', [resolution[0]/2, resolution[1]/10.8], int(resolution[1] / 10.5), colours["grey"], 'calibri', 'c')
        pygame.draw.lines(window, colours["grey"], True, ((0,0), (resolution[0],0),
                                                         (resolution[0],resolution[1]), (0,resolution[1])), int(resolution[1]/54))

        pygame_ui.draw_text(window, '{}x{}'.format(resolutions[res][0], resolutions[res][1]), [resolution[0]/2, resolution[1]/3], int(resolution[1] / 15), colours["grey"], 'calibri', 'c')
        if fullscreen:
            pygame_ui.draw_text(window, 'FULLSCREEN', [resolution[0]/2, resolution[1]/2], int(resolution[1] / 15), colours["grey"], 'calibri', 'c')
        else:
            pygame_ui.draw_text(window, 'WINDOWED', [resolution[0]/2, resolution[1]/2], int(resolution[1] / 15), colours["grey"], 'calibri', 'c')


        #process button presses
        if buttons["back"].highlight(mouse_used):
            mouse_used = True
            action = "main"

        elif used_buttons["res_up"].highlight(mouse_used):
            mouse_used = True
            if res < 2:
                res += 1
            
        elif used_buttons["res_down"].highlight(mouse_used):
            mouse_used = True
            if res > 0:
                res -= 1
            
        elif used_buttons["screen_up"].highlight(mouse_used) or used_buttons["screen_down"].highlight(mouse_used):
            mouse_used = True
            fullscreen = not fullscreen

        elif used_buttons["apply"].highlight(mouse_used):
            resolution = resolutions[res]
            if fullscreen:
                window = pygame.display.set_mode((resolution[0], resolution[1]), pygame.FULLSCREEN)
            else:
                window = pygame.display.set_mode((resolution[0], resolution[1]))
            mouse_used = True

            #reset all sizes
            used_buttons["back"].set_size(resolution[0]/5, resolution[0] / 30)
            used_buttons["apply"].set_size(resolution[0]/5, resolution[0] / 30)
            used_buttons["res_up"].set_size(resolution[1]/54)
            used_buttons["res_down"].set_size(resolution[1]/54)
            used_buttons["screen_up"].set_size(resolution[1]/54)
            used_buttons["screen_down"].set_size(resolution[1]/54)

            #reset all positions
            used_buttons["back"].set_pos([resolution[0]/2, resolution[1] - resolution[0] / 16])
            used_buttons["apply"].set_pos([resolution[0]/2, resolution[1] - resolution[0] / 7.5])
            used_buttons["res_up"].set_pos([resolution[0]/2 - resolution[0]/7, resolution[1]/3])
            used_buttons["res_down"].set_pos([resolution[0]/2 - resolution[0]/7, resolution[1]/3])
            used_buttons["screen_up"].set_pos([resolution[0]/2 - resolution[0]/7, resolution[1]/2])
            used_buttons["screen_down"].set_pos([resolution[0]/2 - resolution[0]/7, resolution[1]/2])

            

        #render all buttons
        for button in used_buttons:
            used_buttons[button].render()

        #check if game is quit
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()

        pygame.display.update()

    return action, mouse_used, resolution, window

def main_menu(colours, window, resolution, border_inset, action, buttons, mouse_used):
    used_buttons = {"boids" : buttons["boids"],
                    "particles" : buttons["particles"],
                    "settings" : buttons["settings"],
                    "quit" : buttons["quit"]
                    }

    start = resolution[1] * 41 / 108
    incriment = resolution[1] * 7 / 54
    used_buttons["settings"].set_pos([resolution[0] / 2, start + incriment * 3])
    used_buttons["quit"].set_pos([resolution[0] / 2, start + incriment * 4])
    
    while action == "main":
        #Reset mouse usage
        if not pygame.mouse.get_pressed()[0]:
            mouse_used = False

        window.fill(colours["light_grey"])

        if buttons["settings"].highlight(mouse_used):
            mouse_used = True
            action = "settings"

        elif buttons["quit"].highlight(mouse_used):
                pygame.quit()
                quit()

        elif buttons["boids"].highlight(mouse_used):
            mouse_used = True
            action = "boids_s"

        elif buttons["particles"].highlight(mouse_used):
            mouse_used = True
            action = "particles_m"
        

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()

        for button in used_buttons:
            used_buttons[button].render()

        pygame.draw.lines(window, colours["grey"], True, ((0,0), (resolution[0],0),
                                                         (resolution[0],resolution[1]), (0,resolution[1])), int(resolution[1]/54))
        pygame_ui.draw_text(window, 'PHYSICS STUDIO', [resolution[0]/2, resolution[1]/10.8], int(resolution[1] / 10.5), colours["grey"], 'calibri', 'c')
        pygame_ui.draw_text(window, 'Alex Elwood | BETA (0.3.6)', [resolution[0] / 1.007, resolution[1]/1.02], int(resolution[1] / 56), colours["grey"], 'calibri', 'mr')
        pygame.display.update()

    return action, mouse_used

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    phy_consts = {"g" : 500.0,
                  "air_den" : 0.01,
                  "co_rest" : 0.85,
                  "co_fric" : 0.1,
                  "throw_strength" : 50}

    colours = {"white" : [255,255,255],
               "red" : [255,0,0],
               "blue" : [0,0,255],
               "light_blue" : [0, 255, 255],
               "green" : [0, 255, 0],
               "yellow" : [255,255,0],
               "black" : [0,0,0],
               "grey" : [70, 70, 70],
               "light_grey" : [150, 150, 150],
               "pink" : [255, 0, 255],
               "purple" : [102, 0, 102],
               "dark_green" : [0, 102, 0],
               "orange" : [255,102,0]}

    clock = pygame.time.Clock()
    resolution = [1920, 1080]
    border_inset = resolution[1]/36
    pygame.init()
    window = pygame.display.set_mode((resolution[0], resolution[1]))
    pygame.display.set_caption('Physics')

    mouse_used = False
    dyn_objects = []

    sta_objects, sliders, buttons = init_objects(window, resolution, border_inset, phy_consts, colours)

    action = "main"
    while True:
        if action == "main":
            action, mouse_used = main_menu(colours, window, resolution, border_inset, action, buttons, mouse_used)
        elif action == "particles_m":
            action, mouse_used, dyn_objects = particles.menu(colours, window, resolution, border_inset, action, buttons, mouse_used, phy_consts)
        elif action == "particles_s":
            action = particles.simulation(window, clock, colours, resolution, dyn_objects, sta_objects, sliders, phy_consts, action)
        elif action == "settings":
            action, mouse_used, resolution, window = settings(colours, window, resolution, border_inset, action, buttons, mouse_used)
        elif action == "boids_m":
            action, mouse_used = boids.menu()
        elif action == "boids_s":
            action, mouse_used = boids.simulation(colours, clock, window, resolution, border_inset, action, buttons, mouse_used)
        
            
if __name__ == "__main__":
    main()
