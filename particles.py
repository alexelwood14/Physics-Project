import pygame
import math
import numpy as np
import random
import pygame_ui
from pygame.locals import *


def render_border(window, resolution, colour, border_inset):
    pygame.draw.rect(window, colour, [0, 0, resolution[0], border_inset])
    pygame.draw.rect(window, colour, [0, resolution[1] - border_inset, resolution[0], border_inset])
    pygame.draw.rect(window, colour, [0, 0, border_inset, resolution[1]])
    pygame.draw.rect(window, colour, [resolution[0] - border_inset, 0, border_inset, resolution[1]])


def energy_check(dyn_objects, prev_energy, gravity, resolution):
    tolerance = 0.1
    energy = 0
    for obj in dyn_objects:
        # Add object kinetic energy
        speed = np.sqrt((obj.get_vel()).dot(obj.get_vel()))
        energy += 0.5 * obj.get_mass() * (speed ** 2)
        # Add object gravitational energy
        energy += obj.get_mass() * gravity * (resolution[1] - obj.get_pos()[1])

    # Check for conservation violation
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


def simulation(window, clock, colours, resolution, dyn_objects, sta_objects, sliders, phy_consts, action):
    border_inset = resolution[1] / 36
    mouse_down = False
    display_debug = False
    paused = False
    energy = 99999999999
    momentum = [0, 0]
    collision_stack = []

    # Set size of all sliders
    sliders["g"].set_size(resolution[1] / 72)
    sliders["throw_strength"].set_size(resolution[1] / 72)
    sliders["air_den"].set_size(resolution[1] / 72)
    sliders["co_rest"].set_size(resolution[1] / 72)
    sliders["co_fric"].set_size(resolution[1] / 72)

    sliders["g"].set_maximum(resolution[0] * 48 / 25)

    # Set position of all slider
    line_spacing = resolution[1] * 7 / 108
    start_pos = [resolution[0] / 1.2, resolution[1] / 12]
    sliders["g"].set_pos([start_pos[0], start_pos[1]])
    sliders["throw_strength"].set_pos([start_pos[0], start_pos[1] + line_spacing * 4])
    sliders["air_den"].set_pos([start_pos[0], start_pos[1] + line_spacing])
    sliders["co_rest"].set_pos([start_pos[0], start_pos[1] + line_spacing * 2])
    sliders["co_fric"].set_pos([start_pos[0], start_pos[1] + line_spacing * 3])

    # Reset border inset
    for dyn in dyn_objects:
        dyn.set_border_inset(border_inset)

    for obj in dyn_objects:
        obj.set_pos([random.uniform(resolution[0] / 9.6, resolution[1] / 0.72),
                     random.uniform(resolution[0] / 9.6, resolution[1] / 1.35)])
        vel = resolution[0] / 3.84
        obj.set_vel([random.uniform(-vel, vel), random.uniform(-vel, vel)])

    while action == "particles_s":
        window.fill(colours["light_grey"])
        frame_time = clock.tick() / 1000

        # Input Processing
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
                    action = "particles_m"

                if event.key == K_ESCAPE:
                    pygame.quit()

        # Find all collisions
        temp = []
        collision_stack = []
        for obj in dyn_objects:
            temp.append(obj)

        for obj in dyn_objects:
            temp.pop(0)
            collision_stack = obj.collision(temp, collision_stack)

        # Process dragging of dynamic objects
        for obj in dyn_objects:
            obj.dragged(mouse_down)

        # Process collisions of all dynamic objects
        if not paused:
            for col in collision_stack:
                col.process(phy_consts)

        # Dynamic object processing
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

        # Check for physics violations
        energy_violation, energy = energy_check(dyn_objects, energy, phy_consts["g"], resolution)
        momentum_violation, momentum = momentum_check(dyn_objects, momentum)

        # Display Debug Data
        if display_debug:
            line_spacing = resolution[1] / 24
            text_size = int(resolution[0] / 72)
            pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                                [resolution[0] / 32, resolution[1] / 14], text_size, colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "gravitational acceleration: {}".format(round(phy_consts["g"], 1)),
                                [resolution[0] / 32, resolution[1] / 14 + line_spacing], text_size, colours["white"],
                                "calibri", "ml")
            pygame_ui.draw_text(window, "air density: {}".format(round(phy_consts["air_den"], 3)),
                                [resolution[0] / 32, resolution[1] / 14 + line_spacing * 2], text_size,
                                colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "coefficient of restitution: {}".format(round(phy_consts["co_rest"], 1)),
                                [resolution[0] / 32, resolution[1] / 14 + line_spacing * 3], text_size,
                                colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "coefficient of friction: {}".format(round(phy_consts["co_fric"], 1)),
                                [resolution[0] / 32, resolution[1] / 14 + line_spacing * 4], text_size,
                                colours["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "throw strength: {}".format(round(phy_consts["throw_strength"], 1)),
                                [resolution[0] / 32, resolution[1] / 14 + line_spacing * 5], text_size,
                                colours["white"], "calibri", "ml")

            if not mouse_down:
                if energy_violation:
                    pygame_ui.draw_text(window, "ENERGY CONSERVATION VIOLATION",
                                        [resolution[0] / 32, resolution[1] / 14 + line_spacing * 6], text_size,
                                        colours["red"], "calibri", "ml")
                if momentum_violation:
                    pygame_ui.draw_text(window, "MOMENTUM CONSERVATION VIOLATION",
                                        [resolution[0] / 32, resolution[1] / 14 + line_spacing * 7], text_size,
                                        colours["red"], "calibri", "ml")

            for obj in dyn_objects:
                obj.force_lines(colours, resolution)

        if paused:
            pygame_ui.draw_text(window, "PAUSED",
                                [resolution[0] / 2, resolution[1] / 2], int(resolution[0] / 24), colours["red"],
                                "calibri", "c")

        pygame.display.update()

    return action


def menu(colours, window, resolution, border_inset, action, buttons, mouse_used, phy_consts):
    mouse_down = False
    used_buttons = {"back": buttons["back"],
                    "initiate": buttons["initiate"],
                    "rand_all": buttons["rand_all"],
                    "rand_colour": buttons["rand_colour"],
                    "rand_radius": buttons["rand_radius"],
                    "rand_mass": buttons["rand_mass"],
                    "uniform": buttons["uniform"],
                    "scroll_bar": buttons["scroll_bar"]}

    # Set Sizes of all used buttons
    used_buttons["back"].set_size(resolution[0] / 5, resolution[0] / 30)
    used_buttons["initiate"].set_size(resolution[0] / 5, resolution[0] / 30)
    used_buttons["rand_all"].set_size(resolution[0] / 5, resolution[1] * 5 / 108)
    used_buttons["rand_colour"].set_size(resolution[0] / 8, resolution[1] / 27)
    used_buttons["rand_radius"].set_size(resolution[0] / 8, resolution[1] / 27)
    used_buttons["rand_mass"].set_size(resolution[0] / 8, resolution[1] / 27)
    used_buttons["uniform"].set_size(resolution[0] / 5, resolution[1] * 5 / 108)
    used_buttons["scroll_bar"].reset_size(resolution[1])

    # Set locations of all used buttons
    start = resolution[1] * 47 / 108
    increment = resolution[1] * 7 / 54

    used_buttons["back"].set_pos([resolution[1] / 3.6, start + increment * 3])
    used_buttons["initiate"].set_pos([resolution[1] / 3.6, start + increment * 2])
    used_buttons["rand_all"].set_pos([resolution[1] / 3.6, start + increment])
    used_buttons["rand_colour"].set_pos([resolution[1] / 1.35, resolution[1] - resolution[1] / 10.8])
    used_buttons["rand_radius"].set_pos([resolution[1] / 0.9, resolution[1] - resolution[1] / 10.8])
    used_buttons["rand_mass"].set_pos([resolution[0] / 1.2, resolution[1] - resolution[1] / 10.8])
    used_buttons["uniform"].set_pos([resolution[1] / 3.6, start])
    used_buttons["scroll_bar"].set_pos([resolution[0] - resolution[0] * 3 / 128, resolution[1] / 2])
    buttons["add_creator"].set_pos([resolution[0] / 1.55, resolution[1] / 13.5])

    creators = []
    increment = resolution[1] / 10.8
    max_balls = 25
    initial_pos = resolution[1] / 13.5
    creators.append(
        pygame_ui.Ball_Creator(window, [resolution[0] / 1.55, initial_pos + increment * len(creators)], colours,
                               resolution))
    buttons["add_creator"].set_pos([resolution[0] / 1.55, initial_pos + increment * (len(creators))])
    dyn_objects = []

    while action == "particles_m":
        # Reset mouse usage
        if not pygame.mouse.get_pressed()[0]:
            mouse_used = False

        window.fill(colours["light_grey"])

        # Process single buttons
        if used_buttons["back"].highlight(mouse_used):
            mouse_used = True
            action = "main"

        elif used_buttons["initiate"].highlight(mouse_used):
            mouse_used = True
            action = "particles_s"

            for creator in creators:
                mass, radius, colour = creator.get_attributes()
                dyn_objects.append(Sphere(window, border_inset, phy_consts, mass, radius, colour))

        # Sets all ball attributes to a random value
        elif used_buttons["rand_all"].highlight(mouse_used):
            for creator in creators:
                creator.set_mass(random.randint(1, 1000))
                creator.set_colour(random.randint(0, 8))
                creator.set_radius(random.randint(1, int(resolution[1] / 10.8)))
            mouse_used = True

        # Randomises the colour of all balls
        elif used_buttons["rand_colour"].highlight(mouse_used):
            for creator in creators:
                creator.set_colour(random.randint(0, 8))
            mouse_used = True

        # Randomises the mass of all balls
        elif used_buttons["rand_mass"].highlight(mouse_used):
            for creator in creators:
                creator.set_mass(random.randint(1, 1000))
            mouse_used = True

        # Randomises the radius of all balls
        elif used_buttons["rand_radius"].highlight(mouse_used):
            for creator in creators:
                creator.set_radius(random.randint(1, int(resolution[1] / 10.8)))
            mouse_used = True

        # Sets all of the balls to the same as the first ball
        elif used_buttons["uniform"].highlight(mouse_used):
            mass, radius, colour = creators[0].get_attributes()
            colour = creators[0].get_colour()
            for creator in creators:
                creator.set_mass(mass)
                creator.set_colour(colour)
                creator.set_radius(int(radius))
            mouse_used = True

        elif buttons["add_creator"].highlight(mouse_used, resolution) and len(creators) <= max_balls:
            mouse_used = True
            creators.append(
                pygame_ui.Ball_Creator(window, [resolution[0] / 1.55, list_pos + increment * len(creators)], colours,
                                       resolution))
            buttons["add_creator"].set_pos([resolution[0] / 1.55, initial_pos + increment * (len(creators))])

        # Process scroll bar movement
        slider_pos = used_buttons["scroll_bar"].dragging()
        offscreen = len(creators) - 8

        if 0 < offscreen <= 9:
            used_buttons["scroll_bar"].set_size(resolution[1] / 1.08 / (offscreen + 1))
            list_pos = initial_pos - slider_pos * offscreen * increment
        elif offscreen >= 10:
            used_buttons["scroll_bar"].set_size(resolution[1] / 1.08 / 10)
            list_pos = initial_pos - slider_pos * offscreen * increment
        else:
            used_buttons["scroll_bar"].set_size(resolution[1] / 1.08)
            list_pos = initial_pos

        for creator in range(len(creators)):
            creators[creator].set_pos([resolution[0] / 1.55, list_pos + increment * creator], resolution)

        buttons["add_creator"].set_pos([resolution[0] / 1.55, list_pos + increment * len(creators)])

        # Render creators
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

        # Render Overlays
        pygame.draw.rect(window, colours["light_grey"],
                         [resolution[1] / 1.8, resolution[1] / 216 * 187, resolution[1] / 6 * 7,
                          resolution[1] / 72 * 11])
        pygame.draw.lines(window, colours["grey"], True, ((0, 0), (resolution[0], 0),
                                                          (resolution[0], resolution[1]), (0, resolution[1])),
                          int(resolution[1] / 54))
        pygame.draw.line(window, colours["grey"], [resolution[1] / 1.8, 0], [resolution[1] / 1.8, resolution[1]],
                         int(resolution[1] / 108))
        pygame.draw.line(window, colours["grey"], [0, resolution[1] / 3.6], [resolution[1] / 1.8, resolution[1] / 3.6],
                         int(resolution[1] / 108))
        pygame_ui.draw_text(window, 'PARTICLE', [resolution[1] / 3.6, resolution[1] / 10.8], int(resolution[1] / 10.5),
                            colours["grey"], 'calibri', 'c')
        pygame_ui.draw_text(window, 'SIMULATOR', [resolution[1] / 3.6, resolution[1] / 5.4], int(resolution[1] / 10.5),
                            colours["grey"], 'calibri', 'c')

        # Render single buttons
        for button in used_buttons:
            buttons[button].render()

        if del_creator != -1:
            creators.pop(del_creator)
            buttons["add_creator"].set_pos([resolution[0] / 1.55, initial_pos + increment * (len(creators))])
            for creator in range(len(creators)):
                creators[creator].set_pos([resolution[0] / 1.55, initial_pos + increment * creator], resolution)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()

        pygame.display.update()

    return action, mouse_used, dyn_objects


class Dynamic_object:
    def __init__(self, window, border_inset, phy_consts, mass, colour):
        self.phy_consts = phy_consts
        self.window = window
        self.border_inset = border_inset
        self.pos = np.array([0.0, 0.0])
        self.vel = np.array([0.0, 0.0])
        self.acc = np.array([0.0, self.phy_consts["g"]])
        self.mass = mass
        self.grabbed = False
        self.on_ground = False
        self.ground_col = False
        self.movements = []
        self.colour = colour
        self.col_vel = np.array([0.0, 0.0])
        self.cols = []

    def dynamics(self, frame_time, resolution):
        if not self.grabbed:
            self.border_collision(self.radius, resolution)
            self.drag = (self.vel ** 2) * self.phy_consts["air_den"] / float(self.mass)

            if self.vel[0] > 0:
                self.drag[0] *= -1
            if self.vel[1] > 0:
                self.drag[1] *= -1

            self.acc = np.array([self.drag[0], self.drag[1]])
            if not self.on_ground or self.cols[len(self.cols) - 1] != 0:
                self.acc[1] += self.phy_consts["g"]
                self.vel += self.acc * frame_time
                self.fric = 0.0

            else:
                if self.vel[0] >= 0:
                    self.fric = -self.phy_consts["co_fric"] * self.phy_consts["g"]
                else:
                    self.fric = self.phy_consts["co_fric"] * self.phy_consts["g"]
                self.acc[0] += self.fric
                self.vel[0] += self.acc[0] * frame_time
                self.vel[1] = 0.0

            self.pos += self.vel * frame_time

        self.validate_position(resolution)

    def validate_position(self, resolution):
        max_pos = 99999
        if self.pos[0] < -max_pos or self.pos[0] > resolution[0] + max_pos or self.pos[1] < -max_pos or self.pos[1] > \
                resolution[1] + max_pos:
            self.pos = np.array([resolution[0] / 2, resolution[1] / 2])

    def dragging(self, mouse_pos):
        self.grabbed = True
        self.on_ground = False
        prev_pos = self.pos
        self.pos = np.array([float(mouse_pos[0]), float(mouse_pos[1])])

        self.movements.append(self.pos - prev_pos)
        while len(self.movements) >= 10:
            self.movements.pop(0)

        vel = np.array([0.0, 0.0])
        for move in self.movements:
            vel += move
        vel *= self.phy_consts["throw_strength"]

        self.vel = vel
        self.acc = np.array([0.0, 0.0])

    def border_collision(self, size, resolution):
        if self.pos[1] >= resolution[1] - size - self.border_inset:
            self.on_ground = False
            self.pos[1] = resolution[1] - size - self.border_inset
            self.vel[1] = -self.vel[1] * self.phy_consts["co_rest"]
            self.ground_col = True

        elif self.pos[1] <= size + self.border_inset:
            self.pos[1] = size + self.border_inset
            self.vel[1] = -self.vel[1] * self.phy_consts["co_rest"]
            self.ground_col = False
        else:
            self.ground_col = False

        if self.pos[0] >= resolution[0] - size - self.border_inset:
            self.pos[0] = resolution[0] - size - self.border_inset
            self.vel[0] = -self.vel[0] * self.phy_consts["co_rest"]

        elif self.pos[0] <= size + self.border_inset:
            self.pos[0] = size + self.border_inset
            self.vel[0] = -self.vel[0] * self.phy_consts["co_rest"]

    def force_lines(self, colours, resolution):
        pygame.draw.line(self.window, colours["red"], self.pos, self.pos + self.drag / resolution[0] * 640, 3)
        pygame.draw.line(self.window, colours["blue"], self.pos,
                         [self.pos[0], self.pos[1] + self.phy_consts["g"] / resolution[0] * 640], 3)
        if abs(self.vel[0]) > 8:
            pygame.draw.line(self.window, colours["yellow"], self.pos,
                             [self.pos[0] + self.fric / resolution[0] * 640, self.pos[1]], 3)
        if self.on_ground or self.ground_col:
            pygame.draw.line(self.window, colours["green"], self.pos,
                             [self.pos[0], self.pos[1] - self.phy_consts["g"] / resolution[0] * 640], 3)

    def set_pos(self, pos):
        self.pos = np.array(pos)

    def get_pos(self):
        return self.pos

    def set_vel(self, vel):
        self.vel = np.array(vel)

    def get_vel(self):
        return self.vel

    def set_acc(self, acc):
        self.acc = np.array(acc)

    def get_mass(self):
        return self.mass

    def set_mass(self, mass):
        self.mass = mass

    def set_phy_consts(self, phy_consts):
        self.phy_consts = phy_consts

    def set_border_inset(self, border_inset):
        self.border_inset = border_inset


class Static_object:
    def __init__(self, window, colour):
        self.window = window
        self.pos = np.array([0, 0])
        self.colour = colour

    def set_pos(self, pos):
        self.pos = np.array(pos)


class Square(Dynamic_object):
    def __init__(self, window, border_inset, phy_consts, mass, size, colour):
        super().__init__(window, border_inset, phy_consts, mass, colour)
        self.size = size

    def collision(self, resolution, dyn_objects):
        if not self.grabbed:
            self.border_collision(self.size / 2, resolution)

    def dragged(self, mouse_down):
        if mouse_down:
            mouse_pos = pygame.mouse.get_pos()
            if (self.pos[0] + self.size / 2 >= mouse_pos[0] >= self.pos[0] - self.size / 2 and
                    self.pos[1] + self.size / 2 >= mouse_pos[1] >= self.pos[1] - self.size / 2) or self.grabbed:

                self.dragging(mouse_pos)

            else:
                self.movements = []
                self.grabbed = False
        else:
            self.movements = []
            self.grabbed = False

    def render(self):
        pygame.draw.rect(self.window, self.colour,
                         [self.pos[0] - self.size / 2, self.pos[1] - self.size / 2, self.size, self.size])


class Sphere(Dynamic_object):
    def __init__(self, window, border_inset, phy_consts, mass, radius, colour):
        super().__init__(window, border_inset, phy_consts, mass, colour)
        self.radius = radius

    def collision(self, dyn_objects, collision_stack):
        for obj in dyn_objects:
            # loc = Line of Centers
            loc_vec = np.array(obj.get_pos() - self.pos)

            # Calculate if they are colliding
            distance = np.sqrt(loc_vec.dot(loc_vec))
            if distance < self.radius + obj.get_radius() and distance != 0:
                collision_stack.append(Collision(self, obj))

        return collision_stack

    def dragged(self, mouse_down):
        if mouse_down:
            mouse_pos = np.array(pygame.mouse.get_pos())
            if np.sqrt((mouse_pos - self.pos).dot(mouse_pos - self.pos)) <= self.radius or self.grabbed:
                self.dragging(mouse_pos)

            else:
                self.movements = []
                self.grabbed = False
        else:
            self.movements = []
            self.grabbed = False

    def render(self):
        pygame.draw.circle(self.window, self.colour, [int(self.pos[0]), int(self.pos[1])], self.radius)

    def get_radius(self):
        return self.radius

    def set_radius(self, radius):
        self.radius = radius

    def get_cols(self):
        return self.cols

    def add_col(self, col):
        self.cols.append(col)
        while len(col) > 3:
            col.pop(0)


class Collision:
    def __init__(self, obj1, obj2):
        self.obj1 = obj1
        self.obj2 = obj2

    def move_out(self):
        # loc = Line of Centers
        overlap = self.obj1.get_radius() + self.obj2.get_radius() - self.distance
        extra = overlap / 5
        self.obj1.set_pos(self.obj1.get_pos() + (overlap / self.distance / 2) * self.loc_vec + extra)
        self.obj2.set_pos(self.obj2.get_pos() - (overlap / self.distance / 2) * self.loc_vec - extra)

    def convert_to_local(self):
        # Calculate the local axis
        local_x = self.loc_vec / math.sqrt(self.loc_vec[0] ** 2 + self.loc_vec[1] ** 2)
        local_y = np.array([-local_x[1], local_x[0]])

        # Convert obj velocities to local velocities
        self.local_u_obj1 = np.array([np.dot(self.obj1.get_vel(), local_x), np.dot(self.obj1.get_vel(), local_y)])
        self.local_u_obj2 = np.array([np.dot(self.obj2.get_vel(), local_x), np.dot(self.obj2.get_vel(), local_y)])

    def calculate(self, phy_consts):
        # Calculate for obj1
        self.local_v_obj1 = np.array([0.0, 0.0])
        self.local_v_obj1[0] = (((phy_consts["co_rest"] + 1) * self.obj2.get_mass() * self.local_u_obj2[0] +
                                 (self.obj1.get_mass() - phy_consts["co_rest"] * self.obj2.get_mass()) *
                                 self.local_u_obj1[0]) /
                                (self.obj2.get_mass() + self.obj1.get_mass()))
        self.local_v_obj1[1] = self.local_u_obj1[1]

        # Calculate for obj2
        self.local_v_obj2 = np.array([0.0, 0.0])
        self.local_v_obj2[0] = -(((phy_consts["co_rest"] + 1) * self.obj1.get_mass() * self.local_u_obj1[0] +
                                  (self.obj2.get_mass() - phy_consts["co_rest"] * self.obj1.get_mass()) *
                                  self.local_u_obj2[0]) /
                                 (self.obj1.get_mass() + self.obj2.get_mass()))
        self.local_v_obj2[1] = self.local_u_obj2[1]

    def convert_to_global(self):
        self.obj1.set_vel([np.dot(self.local_v_obj1, np.array([1, 0])), np.dot(self.local_v_obj1, np.array([0, 1]))])
        self.obj2.set_vel([np.dot(self.local_v_obj2, np.array([1, 0])), np.dot(self.local_v_obj2, np.array([0, 1]))])

    def record(self):
        self.obj1.add_col().append(self.obj2)
        self.obj2.add_col().append(self.obj1)

    def process(self, phy_consts):
        self.loc_vec = np.array(self.obj1.get_pos() - self.obj2.get_pos())
        self.distance = np.sqrt(self.loc_vec.dot(self.loc_vec))

        if self.distance != 0:
            self.move_out()
            double_hit = False
            for col in self.obj1.get_cols():
                if self.obj2 == col:
                    double_hit = True

            if not double_hit:
                self.convert_to_local()
                self.calculate(phy_consts)
                self.convert_to_global()
