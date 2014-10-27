import pygame
from pygame import Rect
from pygame.color import THECOLORS
from gfx.spritefiller import SpriteFiller


class TopWindow:

    def __init__(self):
        pygame.init()

        size = window_width, window_height = 1200, 1000
        self.window = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.frames_per_second = 60
        self.collisionSprite = pygame.sprite.Sprite()  # Dummy sprite for draw block collision detection
        self.active_object_list = pygame.sprite.Group()
        self.drawing_block = None
        self.drawing_start_pos = [0, 0]
        self.mouse_last_pos = [0, 0]

    def run_event_loop(self):

        while self.check_events():
            self.draw(self.window)
            self.clock.tick(self.frames_per_second)

        pygame.quit()

    def draw(self, surface):
            self.window.fill(THECOLORS['black'])
            self.active_object_list.draw(surface)
            if self.drawing_block:
                pygame.draw.rect(surface, THECOLORS['red'], self.drawing_block.rect, 1)
            pygame.display.update()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if not self.check_key_events(event):
                return False
            self.check_mouse_events(event)
        return True

    def check_key_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

            if event.key == pygame.K_RETURN:
                for platform in self.active_object_list:
                    print "["+",".join([`platform.rect.x`, `platform.rect.y`,
                                        `platform.rect.width`, `platform.rect.height`])+", grass],"
            if event.key == pygame.K_BACKSPACE:
                list_sprites = self.active_object_list.sprites()
                if list_sprites:
                    self.active_object_list.remove(list_sprites[-1])
        return True

    def check_mouse_events(self, event):
        mouse_pos = mouse_x, mouse_y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION:
            moving_right = mouse_x > self.drawing_start_pos[0]
            moving_left = mouse_x < self.drawing_start_pos[0]
            moving_up = mouse_y < self.drawing_start_pos[1]
            moving_down = mouse_y > self.drawing_start_pos[1]
            if self.drawing_block:
                draw_start_x, draw_start_y = [self.drawing_block.rect.x, self.drawing_block.rect.y]
                width = mouse_pos[0] - self.drawing_start_pos[0]
                height = mouse_pos[1] - self.drawing_start_pos[1]
                if width < 0:
                    width = abs(width)
                    draw_start_x = mouse_x
                if height < 0:
                    height = abs(height)
                    draw_start_y = mouse_y

                # Check horizontal collisions
                self.collisionSprite.rect = collisionRect = Rect(draw_start_x, draw_start_y, width, height)
                collision_list = pygame.sprite.spritecollide(self.collisionSprite, self.active_object_list, False)
                for collider in collision_list:
                    if collider == self.drawing_block:  # Can collide with itself
                        continue
                    if moving_right and collisionRect.left < collider.rect.left:
                        width = min(collider.rect.left - self.drawing_start_pos[0], width-1)
                    if moving_left and collisionRect.right > collider.rect.right:
                        draw_start_x = max(collider.rect.right, draw_start_x)
                        width = min(self.drawing_start_pos[0]-collider.rect.right-1, width)

                # Check vertical collisions
                self.collisionSprite.rect = Rect(draw_start_x, draw_start_y, width, height)
                collision_list = pygame.sprite.spritecollide(self.collisionSprite, self.active_object_list, False)
                for collider in collision_list:
                    if collider == self.drawing_block:  # Can collide with itself
                        continue
                    if moving_down:
                        height = min(collider.rect.top - self.drawing_start_pos[1], height-1)
                    if moving_up:
                        draw_start_y = max(collider.rect.bottom, draw_start_y)
                        height = min(self.drawing_start_pos[1]-collider.rect.bottom, height)



                print moving_right, moving_left, moving_up, moving_down
                print width, height
                self.drawing_block.set_position(draw_start_x, draw_start_y)
                self.drawing_block.resize(width, height)

            self.mouse_last_pos = mouse_pos

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.drawing_start_pos = mouse_pos
            self.drawing_block = SpriteFiller(Rect(mouse_pos, (0, 0)), ['data/blocks/snow.png', 'data/blocks/snow-filler.png'])
            if pygame.sprite.spritecollide(self.drawing_block, self.active_object_list, False):
                self.drawing_block = None
            else:
                self.active_object_list.add(self.drawing_block)

        if event.type == pygame.MOUSEBUTTONUP:
            self.drawing_block = None