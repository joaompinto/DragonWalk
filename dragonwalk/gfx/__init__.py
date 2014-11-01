import pygame
from pygame.color import THECOLORS

class Text(object):

    def __init__(self, position, text=None, centered=False):
        self.position = position
        self.centered = True
        self.alpha = 255
        self.font = pygame.font.SysFont("Times New Roman", 30)
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.update()

    def set_text(self, text):
        self.text = text

    def update(self):
        message = self.font.render(self._text, True, THECOLORS['white'])
        message.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
        self.surface = message

    def draw(self, surface):
        x, y = self.position
        if self.centered:
            x = surface.get_width()/2 - self.surface.get_rect().width/2
            y = surface.get_height()/2 - self.surface.get_rect().height/2
        surface.blit(self.surface, (x, y))

