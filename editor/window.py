import pygame
from os.path import exists
from glob import glob
from pygame import Rect
from pygame.color import THECOLORS
from gfx.spritefiller import ElasticSpriteFiller, SpriteFiller
from gfx.toolbox import ToolBox

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
        self.drawing_block_image_list = None
        self.hspeed = 0
        self.vspeed = 0
        self.toolbox = toolbox = ToolBox(self.on_toolbox_change, 0, window_height-64)
        self.is_real_scale = False

        for filename in glob('data/blocks/*.png'):
            if "-filler.png" in filename:
                continue
            image_list = [filename]
            filler_image = filename.split(".")[0]+"-filler.png"
            if exists(filler_image):
                image_list.append(filler_image)
            sprite = SpriteFiller(Rect(0, 0, 64, 64), image_list)
            toolbox.add(sprite)

        for filename in glob('data/objects/*.png'):
            sprite = SpriteFiller(Rect(0, 0, 64, 64), [filename], real_scale=True)
            toolbox.add(sprite)

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
            self.toolbox.draw(surface)
            pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if not self.handle_key_events(event):
                return False
            self.handle_mouse_events(event)
            self.toolbox.handle_events(event)
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
            if not self.drawing_block_image_list:
                return
            real_scale = self.is_real_scale
            self.drawing_block = ElasticSpriteFiller(mouse_pos, self.drawing_block_image_list, real_scale)
            collision_list = pygame.sprite.spritecollide(self.drawing_block, self.active_object_list, False)
            if collision_list or event.button == 3:
                self.drawing_block = None
            if event.button == 3:
                if collision_list:
                    block = collision_list[0]
                    self.active_object_list.remove(block)



        if event.type == pygame.MOUSEBUTTONUP:
            if self.drawing_block:
                if self.drawing_block.rect.width > 0 and self.drawing_block.rect.height > 0:
                    self.active_object_list.add(self.drawing_block)
            self.drawing_block = None

    def on_toolbox_change(self, sprite):
        self.drawing_block_image_list = sprite.image_list
        self.is_real_scale = sprite.is_real_scale
