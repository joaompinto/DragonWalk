#!/bin/python
import pygame
"""
    The SpriteFiller will fill a rectangle by repeating images from an input list
    The image list can have the following number of elements:
    1) Repeat vertically and horizontally
    2) Place the first element at the top, and repeat the second element below; repeats horizontally
"""


class SpriteFiller(pygame.sprite.Sprite):

    def __init__(self, rect, image_list):
        super(SpriteFiller, self).__init__()

        # Set top and filler images
        top_image = pygame.image.load(image_list[0]).convert()
        self.top_image = pygame.transform.scale(top_image, (64, 64))
        if len(image_list) > 1:
            filler_image = pygame.image.load(image_list[1]).convert()
            self.filler_image = pygame.transform.scale(filler_image, (64, 64))
        else:
            self.filler_image = top_image

        self.rect = rect
        self._build_image()

    def resize(self, width, height):
        self.rect.width = width
        self.rect.height = height
        self._build_image()

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def _build_image(self):
        self.image = pygame.Surface([self.rect.width, self.rect.height])
        offset_y = 0
        current_image = self.top_image
        while offset_y < self.rect.height:
            offset_x = 0
            while offset_x < self.rect.width:
                self.image.blit(current_image, (offset_x, offset_y), None)
                offset_x += current_image.get_rect().width
            offset_y += current_image.get_rect().height
            current_image = self.filler_image



