import pygame
from pygame.locals import*

def draw_text(window, text, pos, size, colour, fontName, method):
    font = pygame.font.Font(pygame.font.match_font(fontName), size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    
    if method == 'mt':
        text_rect.midtop = (pos[0], pos[1])
    elif method == 'c':
        text_rect.center = (pos[0], pos[1])
    elif method == "ml":
        text_rect.midleft = (pos[0], pos[1])
        
    window.blit(text_surface, text_rect)

#----------------------------------------------------------------------------------------------------------------------------------
class Button():
    def __init__(self, window, pos, size, text_size, text, colour_1, colour_2):
        self.window = window
        self.pos = pos
        self.size = size
        self.aspect = 3.5
        self.colour_1 = colour_1
        self.colour_2 = colour_2
        self.text = text
        self.text_size = text_size
        self.highlighted = False

        self.image = pygame.Surface((self.size, self.size / self.aspect))
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos[0], self.pos[1])

    def render(self):
        if self.highlighted:
            pygame.draw.rect(self.window, self.colour_2, self.rect, int(self.size / 60))
            pygame.draw.polygon(self.window, self.colour_2,
                                [[self.rect[0], self.rect[1]], [self.rect[0], self.rect[1] + self.rect[3]],
                                 [self.rect[0] + self.rect[2], self.rect[1] + self.rect[3]], [self.rect[0] + self.rect[2], self.rect[1]]])
            draw_text(self.window, self.text, [self.pos[0], self.pos[1]],
                      self.text_size, self.colour_1, 'calibri', 'c')

        else:
            pygame.draw.rect(self.window, self.colour_2, self.rect, int(self.size / 60))
            draw_text(self.window, self.text, [self.pos[0], self.pos[1]],
                     self.text_size, self.colour_2, 'calibri', 'c')

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.rect[0] and mouse_pos[0] <= self.rect[0] + self.rect[2] and
            mouse_pos[1] >= self.rect[1] and mouse_pos[1] <= self.rect[1] + self.rect[3]):
            return True
        else:
            return False

    def set_colours(self, colour_1, colour_2):
        self.colour_1 = colour_1
        self.colour_2 = colour_2


class Radio_Button(Button):
    def __init__(self, window, pos, size, text, colour_1, colour_2):
        super().__init__(window, pos, size, text, colour_1, colour_2)

    def highlight(self, selected=""):
        if (self.collision() and pygame.mouse.get_pressed()[0]) or self.text == selected:
            self.highlighted = True
            return self.text
        else:
            self.highlighted = False
            return selected
    

class Single_Button(Button):
    def __init__(self, window, pos, size, text_size, text, colour_1, colour_2):
        super().__init__(window, pos, size, text_size, text, colour_1, colour_2)

    def highlight(self, mouse_used, selected=""):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False

#----------------------------------------------------------------------------------------------------------------------------------
class Arrow_Button():
    def __init__(self, window, pos, size, colour_1, colour_2):
        self.window = window
        self.pos = pos
        self.size = size
        self.colour_1 = colour_1
        self.colour_2 = colour_2
        self.highlighted = False

    def highlight(self, mouse_used=False):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False

    def set_pos(self, pos):
        self.pos = pos

class Up_Arrow(Arrow_Button):
    def __init__(self, window, pos, size, colour_1, colour_2):
        super().__init__(window, pos, size, colour_1, colour_2)

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0] - self.size and mouse_pos[0] <= self.pos[0] + self.size and
            mouse_pos[1] >= self.pos[1] - self.size and mouse_pos[1] <= self.pos[1]):
            return True
        else:
            return False

    def render(self):
        if self.highlighted:
            pygame.draw.polygon(self.window, self.colour_2, [[self.pos[0] - self.size, self.pos[1] - self.size / 4],
                                                             [self.pos[0] + self.size, self.pos[1] - self.size / 4],
                                                             [self.pos[0], self.pos[1] - self.size - self.size / 4]])
            pygame.draw.lines(self.window, self.colour_1, True, [[self.pos[0] - self.size, self.pos[1] - self.size / 4],
                                                                 [self.pos[0] + self.size, self.pos[1] - self.size / 4],
                                                                 [self.pos[0], self.pos[1] - self.size - self.size / 4]], int(self.size / 10))
        else:
            pygame.draw.polygon(self.window, self.colour_1, [[self.pos[0] - self.size, self.pos[1] - self.size / 4],
                                                             [self.pos[0] + self.size, self.pos[1] - self.size / 4],
                                                             [self.pos[0], self.pos[1] - self.size - self.size / 4]])

class Down_Arrow(Arrow_Button):
    def __init__(self, window, pos, size, colour_1, colour_2):
        super().__init__(window, pos, size, colour_1, colour_2)

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0] - self.size and mouse_pos[0] <= self.pos[0] + self.size and
            mouse_pos[1] >= self.pos[1] and mouse_pos[1] <= self.pos[1] + self.size):
            return True
        else:
            return False

    def render(self):
        if self.highlighted:
            pygame.draw.polygon(self.window, self.colour_2, [[self.pos[0] - self.size, self.pos[1] + self.size / 4],
                                                             [self.pos[0] + self.size, self.pos[1] + self.size / 4],
                                                             [self.pos[0], self.pos[1] + self.size + self.size / 4]])
            pygame.draw.lines(self.window, self.colour_1, True, [[self.pos[0] - self.size, self.pos[1] + self.size / 4],
                                                                 [self.pos[0] + self.size, self.pos[1] + self.size / 4],
                                                                 [self.pos[0], self.pos[1] + self.size + self.size / 4]], int(self.size / 10))
        else:
            pygame.draw.polygon(self.window, self.colour_1, [[self.pos[0] - self.size, self.pos[1] + self.size / 4],
                                                             [self.pos[0] + self.size, self.pos[1] + self.size / 4],
                                                             [self.pos[0], self.pos[1] + self.size + self.size / 4]])
    
#----------------------------------------------------------------------------------------------------------------------------------
class Cross_Button():
    def __init__(self, window, pos, size, colour_1, colour_2):
        self.window = window
        self.pos = pos
        self.size = size
        self.colour_1 = colour_1
        self.colour_2 = colour_2
        self.highlighted = False

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0] - self.size and mouse_pos[0] <= self.pos[0] + self.size and
            mouse_pos[1] >= self.pos[1] - self.size and mouse_pos[1] <= self.pos[1] + self.size):
            return True
        else:
            return False

    def highlight(self, mouse_used):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False

    def render(self):
        if self.highlighted:
            pygame.draw.rect(self.window, self.colour_2, [self.pos[0] - self.size, self.pos[1] - self.size, self.size * 2, self.size * 2])
            pygame.draw.polygon(self.window, self.colour_1, [[self.pos[0] - self.size / 2, self.pos[1] - self.size / 2],
                                                             [self.pos[0] - self.size / 4, self.pos[1] - self.size / 2],
                                                             [self.pos[0], self.pos[1] - self.size / 6],
                                                             [self.pos[0] + self.size / 4, self.pos[1] - self.size / 2],
                                                             [self.pos[0] + self.size / 2, self.pos[1] - self.size / 2],
                                                             [self.pos[0] + self.size / 6, self.pos[1]],
                                                             [self.pos[0] + self.size / 2, self.pos[1] + self.size / 2],
                                                             [self.pos[0] + self.size / 4, self.pos[1] + self.size / 2],
                                                             [self.pos[0], self.pos[1] + self.size / 6],
                                                             [self.pos[0] - self.size / 4, self.pos[1] + self.size / 2],
                                                             [self.pos[0] - self.size / 2, self.pos[1] + self.size / 2],
                                                             [self.pos[0] - self.size / 6, self.pos[1]]])
        else:
            pygame.draw.rect(self.window, self.colour_1, [self.pos[0] - self.size, self.pos[1] - self.size, self.size * 2, self.size * 2])
            pygame.draw.polygon(self.window, self.colour_2, [[self.pos[0] - self.size / 2, self.pos[1] - self.size / 2],
                                                             [self.pos[0] - self.size / 4, self.pos[1] - self.size / 2],
                                                             [self.pos[0], self.pos[1] - self.size / 6],
                                                             [self.pos[0] + self.size / 4, self.pos[1] - self.size / 2],
                                                             [self.pos[0] + self.size / 2, self.pos[1] - self.size / 2],
                                                             [self.pos[0] + self.size / 6, self.pos[1]],
                                                             [self.pos[0] + self.size / 2, self.pos[1] + self.size / 2],
                                                             [self.pos[0] + self.size / 4, self.pos[1] + self.size / 2],
                                                             [self.pos[0], self.pos[1] + self.size / 6],
                                                             [self.pos[0] - self.size / 4, self.pos[1] + self.size / 2],
                                                             [self.pos[0] - self.size / 2, self.pos[1] + self.size / 2],
                                                             [self.pos[0] - self.size / 6, self.pos[1]]])

    def set_pos(self, pos):
        self.pos = pos
#----------------------------------------------------------------------------------------------------------------------------------
class Ball_Creator():
    def __init__(self, window, pos, colours):
        self.window = window
        self.pos = pos
        self.colours = colours
        self.colour = 0
        self.radius = 20
        self.mass = 20

        self.ball_colours = [colours["yellow"], colours["orange"], colours["red"],
                        colours["light_blue"], colours["blue"], colours["green"],
                        colours["dark_green"], colours["purple"], colours["pink"]]
        
        self.delete = Cross_Button(window, [pos[0] + 560, pos[1]], 30, colours["red"], colours["white"])
        
        self.colour_up = Up_Arrow(window, [pos[0] - 500, pos[1]], 20, colours["light_grey"], colours["grey"])
        self.colour_down = Down_Arrow(window, [pos[0] - 500, pos[1]], 20, colours["light_grey"], colours["grey"])
        
        self.radius_up = Up_Arrow(window, [pos[0], pos[1]], 20, colours["light_grey"], colours["grey"])
        self.radius_down = Down_Arrow(window, [pos[0], pos[1]], 20, colours["light_grey"], colours["grey"])
        
        self.mass_up = Up_Arrow(window, [pos[0] + 380, pos[1]], 20, colours["light_grey"], colours["grey"])
        self.mass_down = Down_Arrow(window, [pos[0] + 380, pos[1]], 20, colours["light_grey"], colours["grey"])

    def highlight(self, mouse_used):
        if self.delete.highlight(mouse_used):
            return True, True
        
        elif self.colour_up.highlight(mouse_used):
            self.colour += 1
            if self.colour > len(self.ball_colours) - 1:
                self.colour = 0
            return True, False
        elif self.colour_down.highlight(mouse_used):
            self.colour -= 1
            if self.colour < 0:
                self.colour = len(self.ball_colours) - 1
            return True, False
                
        elif self.mass_up.highlight() and self.mass < 999:
            self.mass += 1
            return True, False
        elif self.mass_down.highlight() and self.mass > 1:
            self.mass -= 1
            return True, False
            
        elif self.radius_up.highlight() and self.radius < 100:
            self.radius += 1
            return True, False
        elif self.radius_down.highlight() and self.radius > 10:
            self.radius -= 1
            return True, False
        return False, False

    def render(self):
        pygame.draw.rect(self.window, self.colours["grey"], [self.pos[0] - 600, self.pos[1] - 40, 1200, 80])
        if self.radius >= 35:
            pygame.draw.circle(self.window, self.ball_colours[self.colour], [int(self.pos[0] - 560), int(self.pos[1])], 35)
        else:
            pygame.draw.circle(self.window, self.ball_colours[self.colour], [int(self.pos[0] - 560), int(self.pos[1])], self.radius)
        draw_text(self.window, "RADIUS: {}".format(self.radius), [self.pos[0] - 370, self.pos[1] + 3], 64, self.colours["white"], "calibri", "ml")
        draw_text(self.window, "MASS: {}".format(self.mass), [self.pos[0] + 60, self.pos[1] + 3], 64, self.colours["white"], "calibri", "ml")
        self.delete.render()
        self.colour_up.render()
        self.colour_down.render()
        self.mass_up.render()
        self.mass_down.render()
        self.radius_up.render()
        self.radius_down.render()

    def get_attributes(self):
        return self.mass, self.radius, self.mass

    def set_pos(self, pos):
        self.pos = pos
        self.delete.set_pos([pos[0] + 560, pos[1]])

        self.colour_up.set_pos([pos[0] - 500, pos[1]])
        self.colour_down.set_pos([pos[0] - 500, pos[1]])

        self.radius_up.set_pos([pos[0], pos[1]])
        self.radius_down.set_pos([pos[0], pos[1]])

        self.mass_up.set_pos([pos[0] + 380, pos[1]])
        self.mass_down.set_pos([pos[0] + 380, pos[1]])

class Add_Creator():
    def __init__(self, window, pos, colours):
        self.window = window
        self.pos = pos
        self.colours = colours
        self.highlighted = False

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0] - 600 and mouse_pos[0] <= self.pos[0] + 600 and
            mouse_pos[1] >= self.pos[1] - 40 and mouse_pos[1] <= self.pos[1] + 40):
            return True
        else:
            return False

    def render(self):
        if self.highlighted:
            pygame.draw.rect(self.window, self.colours["light_grey"], [self.pos[0] - 600, self.pos[1] - 40, 1200, 80])
            pygame.draw.rect(self.window, self.colours["grey"], [self.pos[0] - 600, self.pos[1] - 40, 1200, 80], 4)

        else:
            pygame.draw.rect(self.window, self.colours["grey"], [self.pos[0] - 600, self.pos[1] - 40, 1200, 80])

        pygame.draw.polygon(self.window, self.colours["green"], [[self.pos[0] - 7, self.pos[1] - 30],
                                                                 [self.pos[0] + 7, self.pos[1] - 30],
                                                                 [self.pos[0] + 7, self.pos[1] - 7],
                                                                 [self.pos[0] + 30, self.pos[1] - 7],
                                                                 [self.pos[0] + 30, self.pos[1] + 7],
                                                                 [self.pos[0] + 7, self.pos[1] + 7],
                                                                 [self.pos[0] + 7, self.pos[1] + 30],
                                                                 [self.pos[0] - 7, self.pos[1] + 30],
                                                                 [self.pos[0] - 7, self.pos[1] + 7],
                                                                 [self.pos[0] - 30, self.pos[1] + 7],
                                                                 [self.pos[0] - 30, self.pos[1] - 7],
                                                                 [self.pos[0] - 7, self.pos[1] - 7]])

    def highlight(self, mouse_used):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False

    def set_pos(self, pos):
        self.pos = pos
        
#----------------------------------------------------------------------------------------------------------------------------------
class Scroll_Bar():
    def __init__(self, window, pos, colour):
        self.window = window
        self.pos = pos
        self.colour = colour
        self.grabbed = False
        self.slider_pos = 0
        self.slider_size = 200

    def render(self):
        pygame.draw.rect(self.window, self.colour, [self.pos[0] - 20, self.pos[1] - 500, 40, 1000], 4)
        pygame.draw.rect(self.window, self.colour, [self.pos[0] - 20, self.slider_pos + 40, 40, self.slider_size])

    def dragging(self):        
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if (mouse_pos[0] <= self.pos[0] + 40 and mouse_pos[0] >= self.pos[0] and
                mouse_pos[1] <= self.slider_pos + self.slider_size and mouse_pos[1] >= self.slider_pos) or self.grabbed:

                self.grabbed = True

                self.slider_pos = mouse_pos[1] - self.slider_size / 2 - 40
                if self.slider_pos > 1000 - self.slider_size:
                    self.slider_pos = 1000 - self.slider_size
                elif self.slider_pos < 0:
                    self.slider_pos = 0
                    
            else:
                self.grabbed = False
        else:
            self.grabbed = False

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
