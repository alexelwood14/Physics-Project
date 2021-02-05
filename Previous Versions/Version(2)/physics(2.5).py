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
        speed = np.sqrt((obj.get_vel()).dot(obj.get_vel()))
        energy += 0.5 * obj.get_mass() * (speed ** 2)
        #Add object gravitational energy
        energy += obj.get_mass() * gravity * (resolution[1] - obj.get_pos()[1])

    #Check for conservation violation
    if energy > prev_energy + prev_energy * tolerance:
        return True, energy
    else:
        return False, energy

def momentum_check(dyn_objects, prev_momentum):
    tolerance = 0.1
    momentum = [0, 0]
    for obj in dyn_objects:
        momentum[0] += obj.get_mass() * obj.get_vel()[0]
        momentum[1] += obj.get_mass() * obj.get_vel()[1]

    if (abs(momentum[0]) > abs(prev_momentum[0] + prev_momentum[0] * tolerance) or
        abs(momentum[1]) > abs(prev_momentum[1] + prev_momentum[1] * tolerance)):
        return True, momentum
    else:
        return False, momentum

#----------------------------------------------------------------------------------------------------------------------------------
def init_objects(window, resolution, border_inset, phy_consts, colours):
    
    #initiate sliders
    line_spacing = resolution[1] * 7 / 108
    start_pos = [resolution[0]/1.2, resolution[1]/12]
    g_slider = objects.Slider(window, [start_pos[0], start_pos[1]], resolution[0] * 48/25, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Gravitational Acceleration")
    throw_slider = objects.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 4], 50, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Throw Strength")
    air_den_slider = objects.Slider(window, [start_pos[0], start_pos[1] + line_spacing], 0.02, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Air Density")
    co_rest_slider = objects.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 2], 1, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Coefficient of Restitution")
    co_fric_slider = objects.Slider(window, [start_pos[0], start_pos[1] + line_spacing * 3], 0.5, [colours["black"], colours["grey"], colours["white"]], resolution[1] / 72, "Coefficient of Friction")

    #initiate text buttons
    start = resolution[1] * 41 / 108
    incriment = resolution[1] * 7 / 54
    quit_button = pygame_ui.Single_Button(window, [resolution[1] / 3.6, start + incriment * 4],
                                          resolution[0]/5, resolution[0] / 30, "QUIT", colours["light_grey"], colours["grey"])

    initiate_button = pygame_ui.Single_Button(window, [resolution[1] / 3.6, start + incriment * 2],
                                          resolution[0]/5, resolution[0] / 30, "INITIATE", colours["light_grey"], colours["grey"])

    back_button = pygame_ui.Single_Button(window, [resolution[0] - resolution[0] / 8, resolution[1] - resolution[0] / 16],
                                          resolution[0]/5, resolution[0] / 30, "BACK", colours["light_grey"], colours["grey"])

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

    #Initiate scroll bar
    scroll_bar = pygame_ui.Scroll_Bar(window, [resolution[0] - resolution[0] * 3 / 128, resolution[1] / 2], colours["grey"], resolution)
    

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
               "rand_all" : rand_all_button,
               "rand_colour" : rand_colour_button,
               "rand_radius" : rand_radius_button,
               "rand_mass" : rand_mass_button,
               "settings" : settings_button,
               "uniform" : uniform_button,
               "add_creator" : add_creator,
               "scroll_bar" : scroll_bar,
               }          

    return  sta_objects, sliders, buttons

#----------------------------------------------------------------------------------------------------------------------------------
def simulation(window, clock, colours, resolution, border_inset, dyn_objects, sta_objects, sliders, phy_consts, action):
    mouse_down = False
    display_debug = False
    paused = False
    energy = 99999999999
    momentum = [0, 0]
    collision_stack = []

    for obj in dyn_objects:
        obj.set_pos([random.uniform(resolution[0]/9.6,resolution[1]/0.72), random.uniform(resolution[0]/9.6,resolution[1]/1.35)])
        vel = resolution[0]/3.84
        obj.set_vel([random.uniform(-vel,vel), random.uniform(-vel,vel)])
    
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

                if event.key == K_p:
                    if paused:
                        paused = False
                    else:
                        paused = True

                if event.key == K_m:
                    action = "main"
                
                if event.key == K_ESCAPE:
                    pygame.quit()

        #Find all collisions
        temp = []
        collision_stack = []
        for obj in dyn_objects:
            temp.append(obj)

        for obj in dyn_objects:
            temp.pop(0)
            collision_stack = obj.collision(temp, collision_stack)
                    
        #Process dragging of dynamic objects
        for obj in dyn_objects:
            obj.dragged(mouse_down)

        #Process collisions of all dynamic objects
        if not paused:
            for col in collision_stack:
                col.process(phy_consts)

        #Dynamic object processing
        for obj in dyn_objects:
            if not paused:
                obj.dynamics(frame_time, resolution)
            obj.render()

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
                obj.force_lines(colours)

        if paused:
            pygame_ui.draw_text(window, "PAUSED",
                      [resolution[0]/2, resolution[1]/2], int(resolution[0]/24), colours["red"], "calibri", "c")

        pygame.display.update()

    return action

#----------------------------------------------------------------------------------------------------------------------------------
def main_menu(colours, window, resolution, border_inset, action, buttons, mouse_used, phy_consts):
    mouse_down = False
    used_buttons = {"quit" : buttons["quit"],
                    "initiate" : buttons["initiate"],
                    "rand_all" : buttons["rand_all"],
                    "rand_colour" : buttons["rand_colour"],
                    "rand_radius" : buttons["rand_radius"],
                    "rand_mass" : buttons["rand_mass"],
                    "settings" : buttons["settings"],
                    "uniform" : buttons["uniform"],
                    "scroll_bar" : buttons["scroll_bar"]}

    creators = []
    incriment = resolution[1] / 10.8
    max_balls = 25
    initial_pos = resolution[1] / 13.5
    creators.append(pygame_ui.Ball_Creator(window, [resolution[0] /1.55, initial_pos + incriment * len(creators)], colours, resolution))
    buttons["add_creator"].set_pos([resolution[0] /1.55, initial_pos + incriment * (len(creators))])
    dyn_objects = []
    
    while action == "main":
        #Reset mouse usage
        if not pygame.mouse.get_pressed()[0]:
            mouse_used = False

        window.fill(colours["light_grey"])

        #Process single buttons
        if used_buttons["quit"].highlight(mouse_used):
            mouse_used = True
            pygame.quit()
            quit()

        elif used_buttons["initiate"].highlight(mouse_used):
            mouse_used = True
            action = "sim"
            
            for creator in creators:
                mass, radius, colour = creator.get_attributes()
                dyn_objects.append(objects.Sphere(window, border_inset, phy_consts, mass, radius, colour))

        #Sets all ball attributes to a random value
        elif used_buttons["rand_all"].highlight(mouse_used):
            for creator in creators:
                creator.set_mass(random.randint(1, 1000))
                creator.set_colour(random.randint(0, 8))
                creator.set_radius(random.randint(1, int(resolution[1] / 10.8)))
            mouse_used = True

        #Randomises the colour of all balls
        elif used_buttons["rand_colour"].highlight(mouse_used):
            for creator in creators:
                creator.set_colour(random.randint(0, 8))
            mouse_used = True

        #Randomises the mass of all balls
        elif used_buttons["rand_mass"].highlight(mouse_used):
            for creator in creators:
                creator.set_mass(random.randint(1, 1000))
            mouse_used = True

        #Randomises the radius of all balls
        elif used_buttons["rand_radius"].highlight(mouse_used):
            for creator in creators:
                creator.set_radius(random.randint(1, int(resolution[1] / 10.8)))
            mouse_used = True

        #Sets all of the balls to the same as the first ball
        elif used_buttons["uniform"].highlight(mouse_used):
            mass, radius, colour = creators[0].get_attributes()
            colour = creators[0].get_colour()
            for creator in creators:
                creator.set_mass(mass)
                creator.set_colour(colour)
                creator.set_radius(int(radius)) 
            mouse_used = True

        #Opens the settings menu
        elif used_buttons["settings"].highlight(mouse_used):
            mouse_used = True
            action = "settings"

        elif buttons["add_creator"].highlight(mouse_used, resolution) and len(creators) <= max_balls:
            mouse_used = True
            creators.append(pygame_ui.Ball_Creator(window, [resolution[0] /1.55, list_pos + incriment * len(creators)], colours, resolution))
            buttons["add_creator"].set_pos([resolution[0] /1.55, initial_pos + incriment * (len(creators))])

        #Process scroll bar movement
        slider_pos = used_buttons["scroll_bar"].dragging()
        offscreen = len(creators) - 8
        
        if offscreen > 0 and offscreen <= 9:
            used_buttons["scroll_bar"].set_size(resolution[1] / 1.08 / (offscreen + 1))
            list_pos = initial_pos - slider_pos * offscreen * incriment
        elif offscreen >= 10:
            used_buttons["scroll_bar"].set_size(resolution[1] / 1.08 / 10)
            list_pos = initial_pos - slider_pos * offscreen * incriment
        else:
            used_buttons["scroll_bar"].set_size(resolution[1] / 1.08)
            list_pos = initial_pos
            
        for creator in range(len(creators)):
            creators[creator].set_pos([resolution[0] /1.55, list_pos + incriment * creator], resolution)
            
        buttons["add_creator"].set_pos([resolution[0] /1.55, list_pos + incriment * len(creators)])


        #Render creators
        del_creator = -1
        for creator in range(len(creators)):
            if mouse_used:
                temp, delete = creators[creator].highlight(mouse_used, resolution)
            else:
                mouse_used, delete = creators[creator].highlight(mouse_used, resolution)
            if delete:
                del_creator = creator
            creators[creator].render(resolution)
        if len(creators) <= max_balls:
            buttons["add_creator"].render(resolution)

        #Render Overlays
        pygame.draw.rect(window, colours["light_grey"], [resolution[1]/1.8, resolution[1]/216*187, resolution[1]/6*7, resolution[1]/72*11])
        pygame.draw.lines(window, colours["grey"], True, ((0,0), (resolution[0],0),
                                                         (resolution[0],resolution[1]), (0,resolution[1])), int(resolution[1]/54))
        pygame.draw.line(window, colours["grey"], [resolution[1]/1.8, 0], [resolution[1]/1.8, resolution[1]], int(resolution[1]/108))
        pygame.draw.line(window, colours["grey"], [0, resolution[1]/3.6], [resolution[1]/1.8, resolution[1]/3.6], int(resolution[1]/108))
        pygame_ui.draw_text(window, 'PARTICLE', [resolution[1]/3.6, resolution[1]/10.8], int(resolution[1] / 10.5), colours["grey"], 'calibri', 'c')
        pygame_ui.draw_text(window, 'SIMULATOR', [resolution[1]/3.6, resolution[1]/5.4], int(resolution[1] / 10.5), colours["grey"], 'calibri', 'c')

        #Render single buttons
        for button in used_buttons:
            buttons[button].render()

        if del_creator != -1:
            creators.pop(del_creator)
            buttons["add_creator"].set_pos([resolution[0] /1.55, initial_pos + incriment * (len(creators))])
            for creator in range(len(creators)):
                creators[creator].set_pos([resolution[0] /1.55, initial_pos + incriment * creator], resolution)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()

            
        pygame.display.update()

    return action, mouse_used, dyn_objects

def settings(colours, window, resolution, border_inset, action, buttons, mouse_used):
    while action = "settings":
        #Reset mouse usage
        if not pygame.mouse.get_pressed()[0]:
            mouse_used = False

        window.fill(colours["light_grey"])

        

    return active, mouse_used

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
    window = pygame.display.set_mode((resolution[0], resolution[1]), pygame.FULLSCREEN)
    print(pygame.display.toggle_fullscreen())
    pygame.display.set_caption('Physics')

    mouse_used = False
    dyn_objects = []

    sta_objects, sliders, buttons = init_objects(window, resolution, border_inset, phy_consts, colours)

    action = "main"
    while True:
        if action == "main":
            action, mouse_used, dyn_objects = main_menu(colours, window, resolution, border_inset, action, buttons, mouse_used, phy_consts)
        elif action == "sim":
            action = simulation(window, clock, colours, resolution, border_inset, dyn_objects, sta_objects, sliders, phy_consts, action)
        elif action == "settings":
            action, mouse_used = settings(colours, window, resolution, border_inset, action, buttons, mouse_used)
        
            
if __name__ == "__main__":
    main()
