import pygame
from pygame import Rect
from pygame.color import THECOLORS

class SpriteBlock(pygame.sprite.Sprite):

    def __init__(self, (x, y), (width, height), image_list):
        super(SpriteBlock, self).__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        top_image = pygame.image.load(image_list[0]).convert()
        self.top_image = pygame.transform.scale(top_image, (64, 64))
        if len(image_list) > 1:
            fill_image = pygame.image.load(image_list[1]).convert()
            self.fill_image = pygame.transform.scale(fill_image, (64, 64))
        else:
            self.fill_image = top_image
        self.resize(width, height)
        self.set_position(x, y)

    def resize(self, width, height):
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.rect.width = width
        self.rect.height = height
        offset_y = 0
        current_image = self.top_image
        while offset_y < height:
            offset_x = 0
            while offset_x < width:
                self.image.blit(current_image, (offset_x, offset_y), None)
                offset_x += current_image.get_rect().width
            offset_y += current_image.get_rect().height
            current_image = self.fill_image

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y




