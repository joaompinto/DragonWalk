#!/usr/bin/python

import pygame
from gfx.spriteblock import SpriteBlock

if __name__ == "__main__":
    pygame.init()

    size = window_width, window_height = 1200, 1000
    window = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    fps = 60
    black = pygame.Color(0, 0, 0)
    white = pygame.Color(255, 255, 255)
    red = pygame.Color(255, 0, 0)

    window.fill(white)
    pygame.display.update()

    active_object_list = pygame.sprite.Group()
    block1 = SpriteBlock((100, 0), (300, 45), ['data/grass-no-rocks.png', 'data/grass-no-rocks-filler.png'])
    block2 = SpriteBlock((0, 150), (10, 200), ['data/grass-no-rocks.png', 'data/grass-no-rocks-filler.png'])
    active_object_list.add(block1, block2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        window.fill(black)

        active_object_list.draw(window)

        pygame.display.update()
        clock.tick(fps)

    pygame.quit()


