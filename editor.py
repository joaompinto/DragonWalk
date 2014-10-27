#!/usr/bin/python

import pygame
from gfx.spritefiller import SpriteFiller
from pygame import Rect
from pygame.color import THECOLORS

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
                    draw_start_x, draw_start_y = [drawing_block.rect.x, drawing_block.rect.y]
                    width = mouse_pos[0] - pos[0]
                    height = mouse_pos[1] - pos[1]
                    if width < 0:
                        width = abs(width)
                        draw_start_x = mouse_x
                    if height < 0:
                        height = abs(height)
                        draw_start_y = mouse_y
                    drawing_block.set_position(draw_start_x, draw_start_y)
                    drawing_block.resize(width, height)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = mouse_pos
                drawing_block = SpriteFiller(Rect(mouse_pos, (0, 0)), ['data/blocks/snow.png', 'data/blocks/snow-filler.png'])
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
        if drawing_block:
            pygame.draw.rect(window, THECOLORS['red'], drawing_block.rect, 1)
        pygame.display.update()
        clock.tick(fps)

    pygame.quit()


