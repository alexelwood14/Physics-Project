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


class Button():
    def __init__(self, window, pos, size, text, colour_1, colour_2):
        self.window = window
        self.pos = pos
        self.size = size
        self.aspect = 3.5
        self.colour_1 = colour_1
        self.colour_2 = colour_2
        self.text = text
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
                int(self.size/self.aspect/1.4), self.colour_1, 'calibri', 'c')

        else:
            pygame.draw.rect(self.window, self.colour_2, self.rect, int(self.size / 60))
            draw_text(self.window, self.text, [self.pos[0], self.pos[1]],
                     int(self.size/self.aspect/1.4), self.colour_2, 'calibri', 'c')

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
    def __init__(self, window, pos, size, text, colour_1, colour_2):
        super().__init__(window, pos, size, text, colour_1, colour_2)

    def highlight(self, selected=""):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0]:
                return True
        else:
            self.highlighted = False
            return False


def main():
    pass

if __name__ == "__main__":
    main()
