import pygame
from pygame.color import THECOLORS

class ToolBox(object):

    def __init__(self, tool_change_callback, position, size):
        self.toolbox = pygame.sprite.Group()
        self.x, self.y = position
        self.x_pos = -1
        self.tool_change_callback = tool_change_callback
        self.active_tool = None
        self.size = size

    def add(self, other):
        self.x += self.size[0]
        other.rect.left = self.x
        other.rect.top = self.y
        self.toolbox.add(other)


    def draw(self, surface):
        self.toolbox.draw(surface)
        if self.active_tool:
            pygame.draw.rect(surface, THECOLORS['blue'], self.active_tool.rect, 3)

    def handle_events(self, event):
        mouse_pos = event.pos
        for sprite in self.toolbox.sprites():
            if sprite.rect.collidepoint(mouse_pos):
                self.tool_change_callback(sprite)
                self.active_tool = sprite
                return sprite
        return None



