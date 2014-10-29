import pygame
from pygame.color import THECOLORS

class ToolBox(object):

    def __init__(self, tool_change_callback, x, y):
        self.toolbox = pygame.sprite.Group()
        self.x = x
        self.y = y
        self.tool_change_callback = tool_change_callback
        self.active_tool = None

    def add(self, other):
        other.rect.left = self.x
        other.rect.top = self.y
        self.x += other.rect.width
        self.toolbox.add(other)

    def draw(self, surface):
        self.toolbox.draw(surface)
        if self.active_tool:
            pygame.draw.rect(surface, THECOLORS['blue'], self.active_tool.rect, 3)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            for sprite in self.toolbox.sprites():
                if sprite.rect.collidepoint(mouse_pos):
                    self.tool_change_callback(sprite)
                    self.active_tool = sprite



