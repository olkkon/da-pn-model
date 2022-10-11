
import pygame as pg

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHTGREY = (192, 192, 192)

def drawText(surface, fontSize, text, pos, center = True, color = BLACK):
    font = pg.font.SysFont('Arial', fontSize)
    textSurf = font.render(text, True, color)
    
    if center:
        textRect = textSurf.get_rect(center = pos)
        surface.blit(textSurf, textRect)
    else:
        surface.blit(textSurf, pos)

class Button():

    def __init__(self, name, left, top, width, height):
        self.name = name
        self.pos = ((left, top), (width, height))
        # onClick event
        self.action = lambda: print('not assigned')
        self.visible = True
        # if this evaluates to True, the button is disabled
        self.grayCondition = lambda: False

    def left(self):
        return self.pos[0][0]
        
    def top(self):
        return self.pos[0][1]
        
    def width(self):
        return self.pos[1][0]
        
    def height(self):
        return self.pos[1][1]

    def execute(self):
        self.action()
        
    def containsPosition(self, pos):
        return ((self.left() <= pos[0]) and (pos[0] <= self.left() + self.width()) and
                (self.top() <= pos[1]) and (pos[1] <= self.top() + self.height()))
    
    def draw(self, surface):
        if self.grayCondition():
            pg.draw.rect(surface, LIGHTGREY, self.pos)
        else:
            pg.draw.rect(surface, BLACK, self.pos, 1)
            
        drawText(surface, 20, self.name, ((self.left() + self.width() / 2), (self.top() + self.height() / 2)))
                
# taken from https://stackoverflow.com/questions/59236523/trying-creating-dropdown-menu-pygame-but-got-stuck
# slighty modified by me

COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)

class DropDown():

    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pg.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.default = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pg.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pg.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))

    def update(self, event_list):
        mpos = pg.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1
        
    def setDefault(self):
        self.main = self.default
        self.active_option = -1