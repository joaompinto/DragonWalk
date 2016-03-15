#!/bin/python
# -*- coding: utf-8 -*-
import pygame
from pygame import Rect

class ActiveSprite(pygame.sprite.Sprite):
    """
    An active sprite extends the sprite with the size and position properties.
    Changing an object size will trigger it's on_size method
    """

    def __init__(self, position, size):
        super(ActiveSprite, self).__init__()
        self.rect = Rect(position, size)
        self.image = None
        self._resize_count = 0
        self.angle = self.old_angle = 0

    @property
    def position(self):
        return self.rect.x, self.rect.y

    @position.setter
    def position(self, value):
        self.rect.x, self.rect.y = value

    @property
    def size(self):
        return self.rect.size

    @size.setter
    def size(self, value):
        if self._resize_count == 0 or self.rect.size != value:  # Avoid costly resizes
            self.rect.size = value
            self.on_resize()
        self._resize_count += 1

    def on_resize(self):
        pass

class AnimableSprite(ActiveSprite):
    """ An AnimableSprite can use multiple images  """
    def __init__(self, position, size, image_filename_list):
        super(AnimableSprite, self).__init__(position, size)
        self.original_images = []
        for filename in image_filename_list:
            original_file = pygame.image.load(filename).convert_alpha()
            self.original_images.append(original_file)
        self.ratio = float(original_file.get_width()) / original_file.get_height()
        self._selected_image_pos = 0
        self._image_filename_list = image_filename_list
        self.position = position
        self.size = size
        self.on_resize()
        self.angle = self.old_angle = 0

    def on_resize(self):
        super(AnimableSprite, self).on_resize()
        original_image = self.original_images[self._selected_image_pos]



        new_width, new_height = self.rect.size
        #new_width = min(self.rect.width, original_image.get_width())
        #new_height = min(self.rect.height,  original_image.get_height())
        self.image = pygame.transform.smoothscale(original_image, (self.rect.width, self.rect.height))
        if self.angle != self.old_angle:
            self.image = pygame.transform.rotate(original_image, self.angle)
            self.old_angle = self.angle

    def copy(self):
        return AnimableSprite(self.position, self.size, self._image_filename_list)

    @property
    def selected_image_pos(self):
        return self._selected_image_pos

    @selected_image_pos.setter
    def selected_image_pos(self, value):
        if self._selected_image_pos != value:
            self._selected_image_pos = value
            self.on_resize()

    @property
    def images_count(self):
        return len(self.original_images)

    @property
    def image_filename_list(self):
        return self._image_filename_list

    def flip(self, xbool, ybool):
        for i in range(len(self.original_images)):
            self.original_images[i] = pygame.transform.flip(self.original_images[i], xbool, ybool)
        self.on_resize()


class SpriteFiller(ActiveSprite):
    """
        The SpriteFiller will fill a rectangle by repeating images from an input list
        The image list can have the following number of elements:
        1) Repeat vertically and horizontally
        2) Place the first element at the top, and repeat the second element below; repeats horizontally
    """

    def __init__(self, position, size, image_filename_list, unit_size=(60, 60)):
        super(SpriteFiller, self).__init__(position, size)

        self._image_filename_list = image_filename_list
        self.unit_size = unit_size

        # Set top and filler images
        self.top_image = pygame.image.load(image_filename_list[0]).convert_alpha()
        self.top_image = pygame.transform.smoothscale(self.top_image, unit_size)
        if len(image_filename_list) > 1:
            filler_image = pygame.image.load(image_filename_list[1]).convert_alpha()
            self.filler_image = pygame.transform.smoothscale(filler_image, unit_size)
        else:
            self.filler_image = self.top_image
        self.position = position
        self.size = size

    @property
    def image_filename_list(self):
        return self._image_filename_list

    def on_resize(self):
        super(SpriteFiller, self).on_resize()
        self.image = pygame.Surface([self.rect.width, self.rect.height], pygame.SRCALPHA)
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
        return SpriteFiller(self.position, self.size, self._image_filename_list)


class ElasticSprite(object):
    """
    ElasticSprite extends a sprite with a base point set during init, and a moving point that can be adjusted.
    The sprite position and size will be adjusted based on the sprite moving point.
    This is mainly useful for mouse drag based drawing
    """
    def __init__(self, base_position, sprite):
        self.base_position = base_position
        self.moving_position = list(base_position)
        self.sprite = sprite
        self.sprite.position = self.base_position
        self.sprite.size = 0, 0

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
        new_x = self.moving_position[0] if block_delta_x < 0 else self.base_position[0]
        new_y = self.moving_position[1] if block_delta_y < 0 else self.base_position[1]
        self.sprite.position = new_x, new_y
        self.sprite.size = width, height

