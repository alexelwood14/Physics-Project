import pygame
import math
import numpy as np
import random


class boid:
    def __init__(self, window, colour, size, resolution, vision_range):
        self.window = window
        self.main_colour = colour
        self.colour = self.main_colour
        self.size = size
        self.vision_range = vision_range
        self.detected_boids = []

        self.pos = np.array([self.vision_range + random.random() * (resolution[0] - self.vision_range * 2),
                             self.vision_range + random.random() * (resolution[1] - self.vision_range * 2)])
        self.grid_coords = [int(self.pos[0] // self.vision_range), int(self.pos[1] // self.vision_range)]

        self.speed = 100.0
        self.vel = np.array([0.0, 200.0])
        self.acc = np.array([0.0, 0.0])

        self.ang_pos = random.random() * math.pi * 2
        self.ang_vel = 0.0
        self.ang_acc = 0.0

        self.ang_vel_max = 7.0

        self.points_mat = np.array([[0, self.size],
                                    [self.size / 1.7, -self.size],
                                    [0, -self.size / 2],
                                    [-self.size / 1.7, -self.size]])

    def find_angle(self, vec_1, vec_2):
        # Finds the angle between two vectors
        abs_vec_1 = np.sqrt(vec_1.dot(vec_1))
        abs_vec_2 = np.sqrt(vec_2.dot(vec_2))

        temp = np.dot(vec_1, vec_2) / abs_vec_1 / abs_vec_2
        if temp > 1:
            temp = 1
        elif temp < -1:
            temp = -1
        angle = math.acos(temp)

        return angle

    def visible_boids(self, boids, grid):
        self.detected_boids = []
        direction = np.array([0, 0])
        self.ang_vel = 0.0

        # Get all boids that are within grid range
        boids = []
        boids.extend(grid[self.grid_coords[0]][self.grid_coords[1]])

        if self.grid_coords[0] > 0:
            boids.extend(grid[self.grid_coords[0] - 1][self.grid_coords[1]])
            if self.grid_coords[1] > 0:
                boids.extend(grid[self.grid_coords[0] - 1][self.grid_coords[1] - 1])
            if self.grid_coords[1] < len(grid[0]) - 1:
                boids.extend(grid[self.grid_coords[0] - 1][self.grid_coords[1] + 1])

        if self.grid_coords[0] < len(grid) - 1:
            boids.extend(grid[self.grid_coords[0] + 1][self.grid_coords[1]])
            if self.grid_coords[1] > 0:
                boids.extend(grid[self.grid_coords[0] + 1][self.grid_coords[1] - 1])
            if self.grid_coords[1] < len(grid[0]) - 1:
                boids.extend(grid[self.grid_coords[0] + 1][self.grid_coords[1] + 1])

        if self.grid_coords[1] > 0:
            boids.extend(grid[self.grid_coords[0]][self.grid_coords[1] - 1])

        if self.grid_coords[1] < len(grid[0]) - 1:
            boids.extend(grid[self.grid_coords[0]][self.grid_coords[1] + 1])

        for boid in boids:
            if boid != self:
                # calculate distance
                boid_pos = boid.get_pos()
                loc_vec = boid_pos - self.pos
                distance = np.sqrt(loc_vec.dot(loc_vec))

                # check if in vision
                if distance <= self.vision_range:
                    angle = self.find_angle(self.vel, loc_vec)
                    self.detected_boids.append([boid, angle, distance])

    def calc_ang_vel(self):
        average_pos = np.array([0.0, 0.0])
        for boid in self.detected_boids:
            boid_pos = boid[0].get_pos()

            # Faction detection
            if self.main_colour == boid[0].get_colour():
                multiplier = 1
                direction = 1
            else:
                multiplier = 20
                direction = -1

            # Alignment
            if self.main_colour == boid[0].get_colour():
                average_pos += boid_pos
                angle_vel = self.find_angle(self.vel, boid[0].get_vel())
                boid_angle = boid[0].get_ang_pos()
                if self.ang_pos > boid_angle:
                    temp = self.ang_pos - boid_angle
                    if temp >= math.pi:
                        self.ang_vel += angle_vel * 5 * direction
                    else:
                        self.ang_vel -= angle_vel * 5 * direction
                else:
                    temp = boid_angle - self.ang_pos
                    if temp >= math.pi:
                        self.ang_vel -= angle_vel * 5 * direction
                    else:
                        self.ang_vel += angle_vel * 5 * direction

            # Separation
            if self.vel[0] != 0:
                line_height = (self.vel[1] * boid_pos[0] - self.vel[1] * self.pos[0]) / self.vel[0] + self.pos[1]
                if (boid_pos[1] < line_height and self.vel[0] <= 0) or (boid_pos[1] > line_height and self.vel[0] >= 0):
                    self.ang_vel -= boid[1] * self.vision_range / 4 / boid[2] * multiplier

                elif (boid_pos[1] > line_height and self.vel[0] <= 0) or (
                        boid_pos[1] < line_height and self.vel[0] >= 0):
                    self.ang_vel += boid[1] * self.vision_range / 4 / boid[2] * multiplier

            else:
                if boid_pos[0] >= self.pos[0]:
                    self.ang_vel -= boid[1] * self.vision_range / 4 / boid[2] * multiplier
                else:
                    self.ang_vel += boid[1] * self.vision_range / 4 / boid[2] * multiplier

        # Cohesion
        if len(self.detected_boids) != 0:
            average_pos /= len(self.detected_boids)
            if average_pos[0] != 0.0 and average_pos[1] != 0.0:
                vec = average_pos - self.pos
                angle = self.find_angle(self.vel, average_pos)
                if self.vel[0] != 0:
                    line_height = (self.vel[1] * average_pos[0] - self.vel[1] * self.pos[0]) / self.vel[0] + self.pos[1]
                    if (average_pos[1] < line_height and self.vel[0] <= 0) or (
                            average_pos[1] > line_height and self.vel[0] >= 0):
                        self.ang_vel += angle

                    elif (average_pos[1] > line_height and self.vel[0] <= 0) or (
                            average_pos[1] < line_height and self.vel[0] >= 0):
                        self.ang_vel -= angle

                else:
                    if average_pos[0] >= self.pos[0]:
                        self.ang_vel -= angle
                    else:
                        self.ang_vel += angle

    def calc_wall_avoid(self, resolution):
        avoidance_factor = self.vision_range * 50
        if self.pos[0] <= self.vision_range:

            if self.pos[1] <= self.vision_range:
                # On left wall and bottom wall
                distance = self.pos[1]
                vector = np.array([1, 1])
                if ((self.vel[1] >= 0 and self.vel[0] < 0) or (
                        self.vel[0] >= 0 and self.vel[1] >= 0 and self.vel[0] < self.vel[1]) or
                        (self.vel[0] < 0 and self.vel[1] < 0 and abs(self.vel[0]) > abs(self.vel[1]))):
                    avoidance_factor *= -1

            elif self.pos[1] >= resolution[1] - self.vision_range:
                # on left wall and top wall
                distance = resolution[1] - self.pos[1]
                vector = np.array([1, -1])
                if ((self.vel[1] >= 0 and self.vel[0] >= 0) or (
                        self.vel[0] < 0 and self.vel[1] >= 0 and abs(self.vel[0]) < self.vel[1]) or
                        (self.vel[0] >= 0 and self.vel[1] < 0 and self.vel[0] > abs(self.vel[1]))):
                    avoidance_factor *= -1

            else:
                # On left wall
                distance = self.pos[0]
                vector = np.array([1, 0])
                if self.vel[1] >= 0:
                    avoidance_factor *= -1

        elif self.pos[0] >= resolution[0] - self.vision_range:

            if self.pos[1] <= self.vision_range:
                # On right wall and bottom wall
                distance = self.pos[1]
                vector = np.array([-1, 1])
                if ((self.vel[1] >= 0 and self.vel[0] >= 0) or (
                        self.vel[0] < 0 and self.vel[1] >= 0 and abs(self.vel[0]) < self.vel[1]) or
                        (self.vel[0] >= 0 and self.vel[1] < 0 and self.vel[0] > abs(self.vel[1]))):
                    pass
                else:
                    avoidance_factor *= -1

            elif self.pos[1] >= resolution[1] - self.vision_range:
                # On right wall and top wall
                distance = resolution[1] - self.pos[1]
                vector = np.array([-1, -1])
                if ((self.vel[1] >= 0 and self.vel[0] < 0) or (
                        self.vel[0] >= 0 and self.vel[1] >= 0 and self.vel[0] < self.vel[1]) or
                        (self.vel[0] < 0 and self.vel[1] < 0 and abs(self.vel[0]) > abs(self.vel[1]))):
                    pass
                else:
                    avoidance_factor *= -1

            else:
                # On right wall
                distance = resolution[0] - self.pos[0]
                vector = np.array([-1, 0])
                if self.vel[1] >= 0:
                    pass
                else:
                    avoidance_factor *= -1

        elif self.pos[1] <= self.vision_range:
            # On bottom wall
            distance = self.pos[1]
            vector = np.array([0, 1])
            if self.vel[0] >= 0:
                pass
            else:
                avoidance_factor *= -1

        elif self.pos[1] >= resolution[1] - self.vision_range:
            # On top wall
            distance = resolution[1] - self.pos[1]
            vector = np.array([0, -1])
            if self.vel[0] >= 0:
                avoidance_factor *= -1

        else:
            # Not near a wall
            return False

        if distance <= 0:
            distance = 0.0000001
        angle = self.find_angle(self.vel, vector)
        self.ang_vel += angle / distance * avoidance_factor

    def dynamics(self, frame_time, resolution):
        # Angle Calculation
        if self.ang_vel > self.ang_vel_max:
            self.ang_vel = self.ang_vel_max
        elif self.ang_vel < -self.ang_vel_max:
            self.ang_vel = -self.ang_vel_max

        self.ang_vel += self.ang_acc * frame_time
        self.ang_pos += self.ang_vel * frame_time
        if self.ang_pos > 0:
            while self.ang_pos >= math.pi * 2:
                self.ang_pos -= math.pi * 2
        else:
            while self.ang_pos <= 0:
                self.ang_pos += math.pi * 2
        self.ang_mat = np.array([[math.cos(self.ang_pos), -math.sin(self.ang_pos)],
                                 [math.sin(self.ang_pos), math.cos(self.ang_pos)]])

        # Displacement Calculation
        self.vel = np.matmul(self.ang_mat, np.array([0, self.speed]))
        self.pos += self.vel * frame_time

        # Move back into frame
        if self.pos[0] < 0:
            self.pos[0] = resolution[0]
        elif self.pos[0] > resolution[0]:
            self.pos[0] = 0

        if self.pos[1] < 0:
            self.pos[1] = resolution[1]
        elif self.pos[1] > resolution[1]:
            self.pos[1] = 0

        self.grid_coords = [int(self.pos[0] // self.vision_range), int(self.pos[1] // self.vision_range)]

    def render(self, colours, display_debug=False):
        # Debug Rendering
        if display_debug:
            pygame.draw.circle(self.window, colours["yellow"], [int(self.pos[0]), int(self.pos[1])],
                               int(self.vision_range), int(1))

            if len(self.detected_boids) > 0:
                self.colour = colours["green"]
                for boid in self.detected_boids:
                    loc_vec = boid[0].get_pos() - self.pos
                    if np.sqrt(loc_vec.dot(loc_vec)) < self.vision_range:
                        pygame.draw.line(self.window, colours["blue"], self.pos, boid[0].get_pos(), 1)
            else:
                self.colour = self.main_colour
        else:
            self.colour = self.main_colour

        # Normal Rendering
        points = np.matmul(self.ang_mat, np.transpose(self.points_mat))
        points = np.transpose(points)
        pygame.draw.polygon(self.window, self.colour, points + self.pos)

    def get_pos(self):
        return self.pos

    def get_vel(self):
        return self.vel

    def get_grid_coords(self):
        return self.grid_coords

    def get_ang_pos(self):
        return self.ang_pos

    def get_colour(self):
        return self.main_colour
