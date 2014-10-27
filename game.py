#!/usr/bin/python

RIGHT = 1
LEFT = 2

import pygame
from pygame.color import THECOLORS
from pygame import Rect
from gfx.spritefiller import SpriteFiller

class Player(pygame.sprite.Sprite):

    def __init__(self, color=THECOLORS['blue'], width=48, height=64):
        super(Player, self).__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.image.fill(color)
        self.set_properties()
        self.hspeed = 0
        self.face_direction = RIGHT
        self.vspeed = 0
        self.level = None

    def set_properties(self):
        self.rect = self.image.get_rect()
        self.speed = 5

    def set_position(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def set_level(self, level):
        self.level = level
        self.set_position(level.player_start_x, level.player_start_y)

    def set_image(self, filename=None):
        file_image = pygame.image.load(filename).convert_alpha()
        pygame.transform.scale(file_image, (self.rect.width, self.rect.height), self.image)
        self.set_properties()

    def update(self, collidable = pygame.sprite.Group(), event=None):
        self.rect.x += self.hspeed
        self.experience_gravity()

        # Check horizontal collisions
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if self.hspeed > 0:
                self.rect.right = collided_object.rect.left
            if self.hspeed < 0:
                self.rect.left = collided_object.rect.right

        self.rect.y += self.vspeed

        # Check vertical collisions
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if self.vspeed > 0:
                self.rect.bottom = collided_object.rect.top
                self.vspeed = 0
            if self.vspeed < 0:
                self.rect.top = collided_object.rect.bottom
                self.vspeed = 0

        if event:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.hspeed = -self.speed
                if event.key == pygame.K_RIGHT:
                    self.hspeed = self.speed
                if event.key == pygame.K_UP:
                    if len(collision_list) > 0:  # Only jump when hitting in the ground
                        self.vspeed = -self.speed*2

            if event.type == pygame.KEYUP:  # Reset current speed
                if event.key == pygame.K_LEFT:
                    if self.hspeed < 0:
                        self.hspeed = 0
                if event.key == pygame.K_RIGHT:
                    if self.hspeed > 0:
                        self.hspeed = 0

        if self.face_direction == RIGHT and self.hspeed < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.face_direction = LEFT
        if self.face_direction == LEFT and self.hspeed > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.face_direction = RIGHT

    def experience_gravity(self, gravity=.35):
        if self.vspeed == 0:  # Keep applying gravity
            self.vspeed = 1
        else:
            self.vspeed += gravity




class Collectable(pygame.sprite.Sprite):

    def __init__(self,  filename, width=48, height=64):
        super(Collectable, self).__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.set_properties()
        self.set_image(filename)

    def set_properties(self):
        self.rect = self.image.get_rect()

    def set_position(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def set_image(self, filename=None):
        file_image = pygame.image.load(filename).convert_alpha()
        pygame.transform.scale(file_image, (self.rect.width, self.rect.height), self.image)

class Level(object):

    def __init__(self, player_object):
        self.collide_object_list = pygame.sprite.Group()
        self.collect_object_list = pygame.sprite.Group()
        self.player_object = player_object
        self.player_start = self.player_start_x, self.player_start_y = 0, 0
        self.world_shift_x = self.world_shift_y = 0
        self.left_viewbox = window_width/2 - window_width/8
        self.right_viewbox = window_width/2 + window_width/10
        self.up_viewbox = window_height/5
        self.down_viewbox = window_height/2

    def update(self):
        self.collide_object_list.update()
        self.collect_object_list.update()

    def draw(self, window):
        window.fill(THECOLORS['black'])
        self.collide_object_list.draw(window)
        self.collect_object_list.draw(window)

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

        # Scroll left ?
        if self.player_object.rect.x <= self.left_viewbox:
            if self.world_shift_x < 0:  # Not at the left edge
                view_difference = self.left_viewbox - self.player_object.rect.x
                self.player_object.rect.x = self.left_viewbox  # Stop the player movement
                self.shift_world(view_difference, 0)

        if self.player_object.rect.x >= self.right_viewbox:
            if abs(self.world_shift_x)+window_width < 1200:  # Not at the right edge
                view_difference = self.right_viewbox - self.player_object.rect.x
                self.player_object.rect.x = self.right_viewbox  # Stop the player movement
                # Don't allow view_difference to scroll over the right edge
                if abs(self.world_shift_x+view_difference) > 1200-window_width:
                    view_difference = -(1200-window_width-abs(self.world_shift_x))
                self.shift_world(view_difference, 0)

        # Check if needs to scroll up
        if self.player_object.rect.y <= self.up_viewbox:
            if self.world_shift_y < 0:  # Not at the top edge
                view_difference = self.up_viewbox - self.player_object.rect.y
                self.player_object.rect.y = self.up_viewbox  # Stop the player movement
                self.shift_world(0, view_difference)

        if self.player_object.rect.y >= self.down_viewbox:
            if abs(self.world_shift_y)+window_height < 1000:  # Not at the bottom edge:
                view_difference = self.down_viewbox - self.player_object.rect.y
                self.player_object.rect.y = self.down_viewbox  # Stop the player movement
                #  Don't allow view_difference to scroll below the bottom edge
                if abs(self.world_shift_y+view_difference) > 1000-window_height:
                    view_difference = -(1000-window_height-abs(self.world_shift_y))
                self.shift_world(0, view_difference)


    def clear_collected(self, player):
        collide_list = pygame.sprite.spritecollide(player, self.collect_object_list, True)
        if len(collide_list) > 0:
            blop_sound.play()


class Level_01(Level):


    def __init__(self, player_object):
        super(Level_01, self).__init__(player_object)

        self.player_start = self.player_start_x, self.player_start_y = 200, 100

        egg = Collectable('data/blue_egg.png')
        egg.set_position(700, 300)
        self.collect_object_list.add(egg)

        color = pygame.Color(0x66, 0xFF, 0x66)
        grass = ['data/grass-no-rocks.png', 'data/grass-no-rocks-filler.png']
        level = [
            # [x, y, width, height, sprite ]
                [662,518,209,168, grass],
                [390,887,244,37, grass],
                [435,755,47,34, grass],
                [964,722,172,53, grass],
                [259,427,151,233, grass],
                [665,181,216,37, grass],
                [590,716,147,55, grass],
                [439,71,108,30, grass],
                [0,984,1199,15, grass],
                [87,185,216,32, grass],
                [85,342,173,319, grass],
                [816,366,319,54, grass],
                [1067,53,42,199, grass],
                [61,826,252,35, grass],
                [517,365,202,103, grass],
                [397,238,209,34, grass],
        ]

        for x, y, width, height, sprite in level:
            new_block = SpriteFiller(Rect((x, y), (width, height)), sprite)
            self.collide_object_list.add(new_block)


def set_message(text):
    global message, previous_message
    message = font.render(text, True, THECOLORS['black'], THECOLORS['white'])
    previous_message = message

if __name__ == "__main__":
    pygame.init()

    window_size = window_width, window_height = 800, 600
    window = pygame.display.set_mode(window_size, pygame.RESIZABLE)

    pygame.display.set_caption("Platform!")

    white = (255, 255, 255)
    black = pygame.Color(0, 0, 0)
    blop_sound = pygame.mixer.Sound('data/Clinking_Teaspoon-Simon_Craggs-59102891.wav')

    clock = pygame.time.Clock()
    frames_per_second = 60

    active_object_list = pygame.sprite.Group()
    player = Player()
    player.set_image('data/blue-baby-dragon-md.png')
    active_object_list.add(player)

    level_list = []
    level_list.append(Level_01(player))
    current_level_number = 0
    current_level = level_list[current_level_number]
    player.set_level(current_level)


    font = pygame.font.SysFont("Times New Roman", 30)
    message = previous_message = None
    set_message("Use the arrow keys to move the block")
    running = True

    while running:
        event = pygame.event.poll()  # We handle one event per frame
        if event.type == pygame.MOUSEMOTION:  # Ignore mouse events
            continue

        if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

        # Update functions
        player.update(current_level.collide_object_list, event)
        event = None

        current_level.update()

        # Logic Testing
        current_level.run_viewbox()
        current_level.clear_collected(player)

        # Draw everything
        current_level.draw(window)
        active_object_list.draw(window)

        # Delay Framerate
        clock.tick(frames_per_second)

        # Update the screen
        pygame.display.update()

    pygame.quit()