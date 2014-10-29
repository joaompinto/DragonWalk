#!/bin/python
import pygame
from pygame import Rect

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
        self._image_list = image_list
        top_image = pygame.image.load(image_list[0]).convert_alpha()
        self.top_image = pygame.transform.scale(top_image, (64, 64))
        if len(image_list) > 1:
            filler_image = pygame.image.load(image_list[1]).convert()
            self.filler_image = pygame.transform.scale(filler_image, (64, 64))
        else:
            self.filler_image = self.top_image

        self.rect = rect
        self.build_image()

    @property
    def image_list(self):
        return self._image_list

    @property
    def size(self):
        return self.rect.width, self.rect.height

    @size.setter
    def size(self, width, height):

        # Avoid costly image rebuild if there are no changes
        if self.rect.width != width or self.rect.height != height:
            self.rect.width = width
            self.rect.height = height
            self.build_image()

    @property
    def position(self):
        return self.rect.width, self.rect.height

    @position.setter
    def position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def build_image(self):
        self.image = pygame.Surface([self.rect.width, self.rect.height])
        offset_y = 0
        current_image = self.top_image
        print self.top_image, self.filler_image
        while offset_y < self.rect.height:
            offset_x = 0
            while offset_x < self.rect.width:
                self.image.blit(current_image, (offset_x, offset_y), None)
                offset_x += current_image.get_rect().width
            offset_y += current_image.get_rect().height
            current_image = self.filler_image


class ElasticSpriteFiller(SpriteFiller):
    """
    The ElasticSpriteFiller provides a SpriteFiller which is drawn starting at an unmovable base potion
    to a moving position. It is mostly useful for mouse oriented drawing.
    """
    def __init__(self, base_position, image_list):
        super(ElasticSpriteFiller, self).__init__(Rect(base_position, (0, 0)), image_list)
        self.base_position = base_position
        self.moving_position = list(base_position)

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
        :return:
        """
        block_delta_x = self.moving_position[0] - self.base_position[0]
        block_delta_y = self.moving_position[1] - self.base_position[1]
        width, height = abs(block_delta_x), abs(block_delta_y)
        draw_x = self.moving_position[0] if block_delta_x < 0 else self.base_position[0]
        draw_y = self.moving_position[1] if block_delta_y < 0 else self.base_position[1]
        SpriteFiller.position.fset(self, draw_x, draw_y)
        SpriteFiller.size.fset(self, width, height)

