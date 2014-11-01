#!/bin/python
# -*- coding: utf-8 -*-
import pygame
from pygame import Rect

"""
    The SpriteFiller will fill a rectangle by repeating images from an input list
    The image list can have the following number of elements:
    1) Repeat vertically and horizontally
    2) Place the first element at the top, and repeat the second element below; repeats horizontally
"""

class SpriteObject(pygame.sprite.Sprite):

    def __init__(self, place_rect, image_filename):
        super(SpriteObject, self).__init__()
        self.image_filename = image_filename
        self.original_image = pygame.image.load(image_filename).convert_alpha()
        self.rect = place_rect
        self._resize_image()

    @property
    def size(self):
        return self.rect.width, self.rect.height

    @size.setter
    def size(self, size):
        self.rect.width, self.rect.height = size
        self._resize_image()

    @property
    def position(self):
        return self.rect.x, self.rect.y

    @position.setter
    def position(self, position):
        self.rect.x,  self.rect.y = position

    def _resize_image(self):

        # Limit on the image original size
        self.rect.width = min(self.rect.width, self.original_image.get_rect().width)
        self.rect.height = min(self.rect.height, self.original_image.get_rect().height)

        self.image = pygame.transform.scale(self.original_image, (self.rect.width, self.rect.height))

    def copy(self):
        return SpriteObject(Rect(self.rect), self.image_filename)


class SpriteFiller(pygame.sprite.Sprite):

    def __init__(self, rect, image_list):
        super(SpriteFiller, self).__init__()

        # Set top and filler images
        self._image_list = image_list
        self.rect = rect
        self.top_image = pygame.image.load(image_list[0]).convert_alpha()
        self.top_image = pygame.transform.scale(self.top_image, (64, 64))
        if len(image_list) > 1:
            filler_image = pygame.image.load(image_list[1]).convert_alpha()
            self.filler_image = pygame.transform.scale(filler_image, (64, 64))
        else:
            self.filler_image = self.top_image

        self.build_image()

    @property
    def image_list(self):
        return self._image_list

    @property
    def size(self):
        return self.rect.width, self.rect.height

    @size.setter
    def size(self, size):
        width, height = size
        # Avoid costly image rebuild if there are no changes
        if self.rect.width != width or self.rect.height != height:
            self.rect.width = width
            self.rect.height = height
            self.build_image()

    @property
    def position(self):
        return self.rect.x, self.rect.y

    @position.setter
    def position(self, position):
        self.rect.x, self.rect.y = position

    def build_image(self):
        self.image = pygame.Surface([self.rect.width, self.rect.height], pygame.SRCALPHA,)
        offset_y = 0
        current_image = self.top_image
        while offset_y < self.rect.height:
            offset_x = 0
            while offset_x < self.rect.width:
                self.image.blit(current_image, (offset_x, offset_y), None)
                offset_x += current_image.get_rect().width
            offset_y += current_image.get_rect().height
            current_image = self.filler_image

    def copy(self):
        return SpriteFiller(Rect(self.rect), self._image_list)


class ElasticSprite(pygame.sprite.Sprite):
    """
    ElasticSprite extends a sprite with a base point set during init, and a moving point that can be adjusted.
    The sprite position and size will be adjusted based on the sprite moving point.
    This is mainly useful for mouse drag based drawing

    Using composition over inheritance for now -- João Pinto
    """
    def __init__(self, sprite, base_position):
        super(ElasticSprite, self).__init__()
        self.sprite = sprite
        self.base_position = base_position
        self.moving_position = list(base_position)
        self.rect = sprite.rect
        self.image = sprite.image

    @property
    def position(self):
        return self.sprite.position

    @property
    def moving_x(self):
        return self.moving_position[0]

    @property
    def moving_y(self):
        return self.moving_position[1]

    @property
    def base_x(self):
        return self.base_position[0]

    @property
    def base_y(self):
        return self.base_position[1]

    @moving_x.setter
    def moving_x(self, value):
        self.moving_position[0] = value
        self.adjust()

    @moving_y.setter
    def moving_y(self, value):
        self.moving_position[1] = value
        self.adjust()


    def adjust(self):
        """
        Adjust the position and size based on the base_pos / moving_pos vertices
        """
        block_delta_x = self.moving_position[0] - self.base_position[0]
        block_delta_y = self.moving_position[1] - self.base_position[1]
        width, height = abs(block_delta_x), abs(block_delta_y)
        draw_x = self.moving_position[0] if block_delta_x < 0 else self.base_position[0]
        draw_y = self.moving_position[1] if block_delta_y < 0 else self.base_position[1]
        self.sprite.position = draw_x, draw_y
        self.sprite.size = width, height
        self.rect = self.sprite.rect
        self.image = self.sprite.image

