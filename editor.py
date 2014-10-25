#!/usr/bin/python

import pygame
from lib.block import Block
from lib.spriteblock import SpriteBlock

if __name__ == "__main__":
    pygame.init()

    size = window_width, window_height = 1200, 1000
    window = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    fps = 60
    black= pygame.Color(0, 0, 0)
    white = pygame.Color(255, 255, 255)
    red = pygame.Color(255, 0, 0)

    window.fill(white)
    pygame.display.update()

    active_object_list = pygame.sprite.Group()
    to_draw = []
    draw_start_box = False
    drawing_block = None


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = mouse_x, mouse_y = pygame.mouse.get_pos()
                if drawing_block:
                    width = mouse_pos[0] - pos[0]
                    height = mouse_pos[1] - pos[1]
                    if width > -1 and height > -1:
                        drawing_block.resize(width, height)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = mouse_pos
                drawing_block = SpriteBlock(mouse_pos, (0, 0), ['data/grass-no-rocks.png', 'data/soil.png'])
                active_object_list.add(drawing_block)

                draw_start_box = True
            if event.type == pygame.MOUSEBUTTONUP:
                final_pos = mouse_pos
                draw_start_box = False
                drawing_block = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    for platform in active_object_list:
                        print "["+",".join([`platform.rect.x`, `platform.rect.y`, `platform.rect.width`, `platform.rect.height`])+", grass],"
                if event.key == pygame.K_BACKSPACE:
                    list_sprites = active_object_list.sprites()
                    if list_sprites:
                        active_object_list.remove(list_sprites[-1])

        window.fill(black)
        active_object_list.draw(window)
        pygame.display.update()
        clock.tick(fps)

    pygame.quit()


