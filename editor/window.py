import pygame
from pygame import Rect
from pygame.color import THECOLORS
from gfx.spritefiller import ElasticSpriteFiller


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
        self.hspeed = 0
        self.vspeed = 0

    def run_event_loop(self):

        while self.handle_events():
            self.draw(self.window)
            self.clock.tick(self.frames_per_second)

        pygame.quit()

    def draw(self, surface):
            self.window.fill(THECOLORS['black'])
            self.active_object_list.draw(surface)
            if self.drawing_block:
                surface.blit(self.drawing_block.image, self.drawing_block.rect)
                pygame.draw.rect(surface, THECOLORS['red'], self.drawing_block.rect, 1)
            pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if not self.handle_key_events(event):
                return False
            self.handle_mouse_events(event)
        return True

    def handle_key_events(self, event):
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

    def handle_mouse_events(self, event):

        mouse_pos = mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.drawing_block:

            colliding_right = colliding_left = colliding_down = colliding_up = False

            # Apply horizontal speed and check for horizontal collisions
            self.drawing_block.moving_x += self.hspeed

            delta_x = self.drawing_block.moving_x - self.drawing_block.base_x
            collision_list = pygame.sprite.spritecollide(self.drawing_block, self.active_object_list, False)
            for collided_object in collision_list:
                if delta_x > 0:
                    self.drawing_block.moving_x = collided_object.rect.left
                    colliding_right = True
                if delta_x < 0:
                    self.drawing_block.moving_x = collided_object.rect.right
                    colliding_left = True

            # Apply vertical speed and check for vertical collisions
            self.drawing_block.moving_y += self.vspeed

            delta_y = self.drawing_block.moving_y - self.drawing_block.base_y
            collision_list = pygame.sprite.spritecollide(self.drawing_block, self.active_object_list, False)
            for collided_object in collision_list:
                if delta_y > 0: # Work-around for bug in an undetermined collision condition
                    self.drawing_block.moving_y = collided_object.rect.top
                    colliding_down = True
                if delta_y < 0:
                    self.drawing_block.moving_y = collided_object.rect.bottom
                    colliding_up = True

            # If colliding only move in the collision opposite direction
            change = mouse_x - self.drawing_block.moving_x
            if colliding_right:
                if change < 0:
                    self.hspeed = change
            elif colliding_left:
                if change > 0:
                    self.hspeed = change
            else:
                self.hspeed = change

            change = mouse_y - self.drawing_block.moving_y
            if colliding_down:
                if change < 0:
                    self.vspeed = change
            elif colliding_up:
                if change > 0:
                    self.vspeed = change
            else:
                self.vspeed = change

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.drawing_block = ElasticSpriteFiller(mouse_pos, ['data/blocks/grass-no-rocks.png', 'data/blocks/grass-no-rocks-filler.png'])
            collision_list = pygame.sprite.spritecollide(self.drawing_block, self.active_object_list, False)
            if collision_list:
                self.drawing_block = None
                if event.button == 3:
                    block = collision_list[0]
                    self.active_object_list.remove(block)



        if event.type == pygame.MOUSEBUTTONUP:
            if self.drawing_block:
                if self.drawing_block.rect.width > 0 and self.drawing_block.rect.height > 0:
                    self.active_object_list.add(self.drawing_block)
            self.drawing_block = None

