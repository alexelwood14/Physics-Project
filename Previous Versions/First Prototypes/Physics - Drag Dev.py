import pygame, math
from pygame.locals import *

global FPSCLOCK, DISPLAYSURF, BACICFONT

FPS = 60
fpsClock = pygame.time.Clock()
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720
time = 0
g = -0.1
airDensity = 0.0001
blockThrown = False

GREY  = ( 30,  30,   30)
WHITE = ( 255, 255, 255)

pygame.init()
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Physics')
                   
class block(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
        self.y = WINDOWHEIGHT / 2
        self.x = WINDOWWIDTH / 2
        self.rect.center = (self.x, self.y)
        self.uy = 0
        self.vy = 0
        self.direction = 1
        self.timex = 0
        self.timey = 0
        self.nowx = 0
        self.last = ''
        self.first = False
        self.directionX = 1
        self.throwing = False
        self.mousePressed = False
        self.tracking = True
        self.tempx = 0
        self.temp2x = self.x
        self.temp2y = self.y
        self.tempy = 0
        self.timeThrow = 0
        self.a = g
        self.dragCoeff = 1
        self.area = 100
        self.mass = 1
        self.dragConstant = (airDensity * self.dragCoeff * self.area) / 2


    def throw(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mousePressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mousePressed = False
        if ((pygame.mouse.get_pos()[0] <= self.x + 10 and pygame.mouse.get_pos()[0] >= self.x - 10 and pygame.mouse.get_pos()[1] <= self.y + 10 and pygame.mouse.get_pos()[1] >= self.y - 10) or (self.tracking)) and self.mousePressed:
            if self.timeThrow == 0 or (self.temp2x >= 0 and pygame.mouse.get_pos()[0] - self.x <= 0) or (self.temp2x <= 0 and pygame.mouse.get_pos()[0] - self.x >= 0) or (self.temp2y >= 0 and pygame.mouse.get_pos()[1] - self.y <= 0) and (self.temp2y <= 0 and pygame.mouse.get_pos()[1] -self.y >= 0):
                self.tempx = self.x
                self.tempy = self.y
                self.tempTimeThrow = self.timeThrow
            self.temp2x = pygame.mouse.get_pos()[0] - self.x
            self.temp2y = pygame.mouse.get_pos()[1] - self.y
            self.x = pygame.mouse.get_pos()[0]
            self.y = pygame.mouse.get_pos()[1]
            self.rect.center = (self.x, self.y)
            self.timeThrow = self.timeThrow + 1
            self.throwing = True
            self.tracking = True
            return False
        elif self.throwing and not self.mousePressed:
            self.ux = ((self.x - self.tempx) / (self.timeThrow - self.tempTimeThrow)) * 0.3
            self.uy = ((self.y - self.tempy) / (self.timeThrow - self.tempTimeThrow)) * 0.3
            return True
        
    
    def updateY(self):
        
        if (self.uy * (time - self.timey) + 0.5 * self.a * (time - self.timey) ** 2) * self.direction >= 0:
            self.a = ((self.mass * g) - self.dragConstant * (self.vy ** 2)) / (self.mass)
        else:
            self.a = ((self.mass * -g) - self.dragConstant * (self.vy ** 2)) / (self.mass)

        if (pygame.sprite.collide_rect(block, bottomBorder) or pygame.sprite.collide_rect(block, topBorder)) and time - self.timey >= 5:
            self.timey = time
            self.y = self.sCurr
            if pygame.sprite.collide_rect(block, topBorder):
                self.last = 'top'
                self.direction = self.direction * -1
                self.uy = self.vy
            elif pygame.sprite.collide_rect(block, bottomBorder):
                if self.last != 'bottom':
                    self.direction = self.direction * -1
                    self.uy = self.vy
                self.last = 'bottom'

        self.sCurr = (self.uy * (time - self.timey) + 0.5 * (self.a - self.drag) * (time - self.timey) ** 2) * self.direction + self.y
        print(self.sCurr)
        self.rect.center = (self.x, self.sCurr)
        self.vy = self.uy + self.a * (time - self.timey)

        if abs(self.vy) >= 10 and abs(self.vy) < 20:
            R = 255
            G = (255 * ((10 - (abs(self.vy) - 10)) / 10))
        elif abs(self.vy) >= 0 and abs(self.vy) < 10:
            R = int(255 * (abs(self.vy) / 10)) 
            G = 255
        else:
            R = 255
            G = 0
        self.image.fill((R, G, 0))


    def updateX(self):
        if (pygame.sprite.collide_rect(block, leftBorder) or pygame.sprite.collide_rect(block, rightBorder)) and self.nowx != time:
            self.directionX = self.directionX * -1
            self.nowx = time
        self.x = self.x + (self.ux * self.directionX)

               
class border(pygame.sprite.Sprite):
    def __init__(self, posX, posY, sizeX, sizeY):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((sizeX, sizeY))
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)

topBorder = border(0, 0, WINDOWWIDTH, 20)
bottomBorder = border(0, WINDOWHEIGHT - 20, WINDOWWIDTH, 2000)
leftBorder = border(0, 20, 20, WINDOWHEIGHT - 40)
rightBorder = border(WINDOWWIDTH - 20, 20, 20, WINDOWHEIGHT - 20)
block = block()

allSprites = pygame.sprite.Group()
allSprites.add(topBorder, bottomBorder, leftBorder, rightBorder, block)

while True:

    if not blockThrown:
        blockThrown = block.throw()
        DISPLAYSURF.fill(WHITE)
        allSprites.draw(DISPLAYSURF)
        
    elif blockThrown:
        DISPLAYSURF.fill(WHITE)
        block.updateX()
        block.updateY()
        allSprites.draw(DISPLAYSURF)
        time = time + 1

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    fpsClock.tick(FPS)

#g change does not work for the first time
#air resist increases not decreases
#air resistance causes some weierd bugs on initialisation
