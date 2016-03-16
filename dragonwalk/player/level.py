import os
from os.path import exists
from dragonwalk.yattag import Doc, indent
from dragonwalk.gfx.sprites import *
from xml.dom import minidom
import pymunk
import math
from pymunk import Vec2d
from pygame.color import THECOLORS


class Level(object):
    def __init__(self, size, window, player_object,
                 collide_object_list=pygame.sprite.Group(),
                 collect_object_list=pygame.sprite.Group(),
                 background_file=None):
        ### Physics stuff
        self.dynamic_object = []
        space = self.space = pymunk.Space()
        space.gravity = Vec2d(0.0, -800.0)
        window_width, window_height = window.get_width(), window.get_height()
        self.window = window
        self.size = size
        self.window_width, self.window_height = window_width, window_height
        self.player_object = player_object
        self.world_shift_x = self.world_shift_y = 0
        self.left_viewbox = window_width / 2 - window_width / 8
        self.right_viewbox = window_width / 2 + window_width / 10
        self.up_viewbox = window_height / 5
        self.down_viewbox = window_height / 2
        self.collide_object_list = collide_object_list
        self.collect_object_list = collect_object_list
        player_object.level = self
        self.background = None
        self.background_file = background_file
        if background_file:
            self.set_background(background_file)
        self._build_physics_elements()
        self._pos = []

    def backup_pos(self):
        for element in self.collect_object_list:
            self._pos.append((element, element.position))

    def restore_pos(self):
        for element, saved_pos in self._pos:
            element.position = saved_pos
            element.angle = 0

    def flipy(self, y):
        """Small hack to convert chipmunk physics to pygame coordinates"""
        return -y + self.window_height

    def _build_physics_elements(self):
        self.dynamic_object = []
        for element in self.collect_object_list:
            width, height = element.size
            mass = width * height
            if element.is_circle:
                moment = pymunk.moment_for_circle(mass, 0, 100)
                body = pymunk.Body(mass, moment)
                shape = pymunk.Circle(body, width/2)
            else:
                vs = [(-width/2, height/2), (width/2, height/2), (width/2, -height/2), (-width/2, -height/2)]
                moment = pymunk.moment_for_poly(mass, vs)
                body = pymunk.Body(mass, moment)
                shape = pymunk.Poly(body, vs)
            shape.friction = 1
            body.position = element.position[0]+width/2, self.flipy(element.position[1]+height/2)
            body.angle = math.pi
            self.space.add(body, shape)
            self.dynamic_object.append((element, shape))

        static_body = pymunk.Body()
        for element in self.collide_object_list:
            x, y = element.position[0], self.flipy(element.position[1])
            width, height = element.size[0], element.size[1]
            static_lines = [pymunk.Segment(static_body, (x, y), (x+width, y), 0.0),
                            pymunk.Segment(static_body, (x+width, y), (x+width, y-height), 0.0),
                            pymunk.Segment(static_body, (x+width, y-height), (x, y-height), 0.0),
                            pymunk.Segment(static_body, (x, y-height), (x, y), 0.0),
                            ]
            for l in static_lines:
                l.friction = 0.5
            self.space.add(static_lines)

    def set_background(self, filename):
        background = pygame.Surface(self.window.get_size())
        file_image = pygame.image.load(filename).convert()
        pygame.transform.smoothscale(file_image, (background.get_width(), background.get_height()), background)
        self.background = background

    def update(self):
        # self.collide_object_list.update()
        # self.collect_object_list.update()
        ### Update physics
        dt = 1.0 / 60.0
        for x in range(1):
            self.space.step(dt)
        for element, shape in self.dynamic_object:
            x, y = shape.body.position
            y = self.flipy(y)
            element.position = x, y
            element.angle = shape.body.angle

    def draw(self, window):
        if self.background:
            window.blit(self.background, (0, 0))
        else:
            window.fill(pygame.color.THECOLORS['black'])
        self.collide_object_list.draw(window)
        for element, shape in self.dynamic_object:
            p = shape.body.position
            p = Vec2d(p.x, self.flipy(p.y))
            # we need to rotate 180 degrees because of the y coordinate flip
            angle_degrees = math.degrees(shape.body.angle) + 180
            rotated_logo_img = pygame.transform.rotate(element.scaled_image, angle_degrees)

            offset = Vec2d(rotated_logo_img.get_size()) / 2.
            p = p - offset
            window.blit(rotated_logo_img, p)
            # debug draw
            #ps = shape.get_vertices()
            #ps = [(p.x, self.flipy(p.y)) for p in ps]
            #ps += [ps[0]]
            #pygame.draw.lines(window, THECOLORS["red"], False, ps, 1)



        #self.collect_object_list.draw(window)

    def shift_world(self, shift_x, shift_y):
        self.world_shift_x += shift_x
        self.world_shift_y += shift_y

        # Shift objects "in-screen" position
        for each_object in self.collide_object_list:
            each_object.rect.x += shift_x
            each_object.rect.y += shift_y

        for each_object in self.collect_object_list:
            each_object.rect.x += shift_x
            each_object.rect.y += shift_y

    def run_viewbox(self):
        window_width, window_height = self.window_width, self.window_height

        # Scroll left ?
        if self.player_object.rect.x <= self.left_viewbox:
            if self.world_shift_x < 0:  # Not at the left edge
                view_difference = self.left_viewbox - self.player_object.rect.x
                self.player_object.rect.x = self.left_viewbox  # Stop the player movement
                self.shift_world(view_difference, 0)

        if self.player_object.rect.x >= self.right_viewbox:
            if abs(self.world_shift_x) + window_width < self.size[0]:  # Not at the right edge
                view_difference = self.right_viewbox - self.player_object.rect.x
                self.player_object.rect.x = self.right_viewbox  # Stop the player movement
                # Don't allow view_difference to scroll over the right edge
                if abs(self.world_shift_x + view_difference) > self.size[0] - window_width:
                    view_difference = -(self.size[0] - window_width - abs(self.world_shift_x))
                self.shift_world(view_difference, 0)

        # Check if needs to scroll up
        if self.player_object.rect.y <= self.up_viewbox:
            if self.world_shift_y < 0:  # Not at the top edge
                view_difference = self.up_viewbox - self.player_object.rect.y
                self.player_object.rect.y = self.up_viewbox  # Stop the player movement
                self.shift_world(0, view_difference)

        if self.player_object.rect.y >= self.down_viewbox:
            if abs(self.world_shift_y) + window_height < self.size[1]:  # Not at the bottom edge:
                view_difference = self.down_viewbox - self.player_object.rect.y
                self.player_object.rect.y = self.down_viewbox  # Stop the player movement
                #  Don't allow view_difference to scroll below the bottom edge
                if abs(self.world_shift_y + view_difference) > self.size[1] - window_height:
                    view_difference = -(self.size[1] - window_height - abs(self.world_shift_y))
                self.shift_world(0, view_difference)

    def clear_collected(self, player):
        collection_list = pygame.sprite.spritecollide(self.player_object, self.collect_object_list, False)
        for obj in collection_list:
            self.collect_object_list.remove(obj)
        return len(self.collect_object_list) == 0

    def save(self, filename):
        doc, tag, text = Doc().tagtext()
        with tag('level', size=','.join([str(x) for x in self.size])):
            with tag('background', filename=self.background_file):
                pass
            if self.player_object:
                with tag('player', position=','.join([str(x) for x in self.player_object.position])
                        , size=','.join([str(x) for x in self.player_object.sprite.size])
                        , image_list=','.join(self.player_object.sprite.image_filename_list)):
                    pass

            all_object_list = pygame.sprite.Group()
            for sprite in self.collect_object_list:
                all_object_list.add(sprite)
            for sprite in self.collide_object_list:
                all_object_list.add(sprite)

            with tag('map'):
                for obj in all_object_list:
                    if isinstance(obj, SpriteFiller):
                        with tag('spritefiller', position=','.join([str(x) for x in obj.position])
                                , size=','.join([str(x) for x in obj.size])
                                , image_list=','.join(obj.image_filename_list)):
                            pass
                    if isinstance(obj, AnimableSprite):
                        with tag('animablesprite', position=','.join([str(x) for x in obj.position])
                                , size=','.join([str(x) for x in obj.size])
                                , image_list=','.join(obj.image_filename_list)
                                , is_collectable=str(obj.collectable)):
                            pass

        tmp_filename = filename + ".tmp"
        with open(tmp_filename, 'w') as save_file:
            save_file.write(indent(doc.getvalue()))
        if exists(filename):
            os.unlink(filename)
        os.rename(tmp_filename, filename)

    @staticmethod
    def load(window, level_filename):
        collide_object_list = pygame.sprite.Group()
        collect_object_list = pygame.sprite.Group()
        player_object = None
        xmldoc = minidom.parse(level_filename)
        level_size = xmldoc.getElementsByTagName('level')[0].attributes['size'].value

        background = xmldoc.getElementsByTagName('background')[0]
        background_filename = background.attributes['filename'].value
        player = xmldoc.getElementsByTagName('player')

        if player:
            player_info = player[0]
            position = [int(i) for i in player_info.attributes['position'].value.split(',')]
            size = [int(i) for i in player_info.attributes['size'].value.split(',')]
            image_list = player_info.attributes['image_list'].value.split(',')
            sprite = AnimableSprite(position, size, image_list)
            player_object = sprite

        for sprite_info in xmldoc.getElementsByTagName('spritefiller'):
            position = [int(i) for i in sprite_info.attributes['position'].value.split(',')]
            size = [int(i) for i in sprite_info.attributes['size'].value.split(',')]
            image_list = sprite_info.attributes['image_list'].value.split(',')
            sprite = SpriteFiller(position, size, image_list)
            collide_object_list.add(sprite)

        for sprite_info in xmldoc.getElementsByTagName('animablesprite'):
            position = [int(i) for i in sprite_info.attributes['position'].value.split(',')]
            size = [int(i) for i in sprite_info.attributes['size'].value.split(',')]
            image_list = sprite_info.attributes['image_list'].value.split(',')
            sprite = AnimableSprite(position, size, image_list)
            sprite.collectable = (sprite_info.attributes['is_collectable'].value == 'True')
            if sprite.collectable:
                collect_object_list.add(sprite)
            else:
                collide_object_list.add(sprite)

        return Level(level_size, window, player_object, collide_object_list, collect_object_list, background_filename)
