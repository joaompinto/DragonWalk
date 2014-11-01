#!/usr/bin/python

import pygame
from pygame.color import THECOLORS
from pygame import Rect
from gfx.spritefiller import SpriteFiller






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
    global message, previous_   message
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



    pygame.quit()