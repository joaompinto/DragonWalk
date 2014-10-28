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
        self.drawing_base_pos = [0, 0]
        self.drawing_moving_pos = [0, 0]
        self.hspeed = 0
        self.vspeed = 0

    def run_event_loop(self):

        while self.check_events():
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

    def adjust_drawing_block(self):
            block_delta_x = self.drawing_moving_pos[0] - self.drawing_base_pos[0]
            block_delta_y = self.drawing_moving_pos[1] - self.drawing_base_pos[1]
            width, height = abs(block_delta_x), abs(block_delta_y)
            draw_x = self.drawing_moving_pos[0] if block_delta_x < 0 else self.drawing_base_pos[0]
            draw_y = self.drawing_moving_pos[1] if block_delta_y < 0 else self.drawing_base_pos[1]
            self.drawing_block.set_position(draw_x, draw_y)
            self.drawing_block.resize(width, height)
            return draw_x, draw_y, width, height

    def check_mouse_events(self, event):

        mouse_pos = mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.drawing_block:

            colliding_right = colliding_left = colliding_down = colliding_up = False

            # Apply horizontal speed
            self.drawing_moving_pos[0] += self.hspeed
            draw_x, draw_y, width, height = self.adjust_drawing_block()
            block_delta_x = self.drawing_moving_pos[0] - self.drawing_base_pos[0]
            collision_list = pygame.sprite.spritecollide(self.drawing_block, self.active_object_list, False)
            print self.drawing_block.rect.width
            for collided_object in collision_list:
                if block_delta_x > 0:
                    width = collided_object.rect.left - draw_x
                    self.drawing_moving_pos[0] = collided_object.rect.left
                    self.drawing_block.resize(width, height)
                    colliding_right = True
                if block_delta_x < 0:
                    self.drawing_moving_pos[0] = collided_object.rect.right
                    self.drawing_block.resize(width, height)
                    colliding_left = True

            self.drawing_moving_pos[1] += self.vspeed
            draw_x, draw_y, width, height = self.adjust_drawing_block()
            print "After adjust drawing", self.drawing_block.rect.width
            block_delta_y = self.drawing_moving_pos[1] - self.drawing_base_pos[1]
            collision_list = pygame.sprite.spritecollide(self.drawing_block, self.active_object_list, False)
            for collided_object in collision_list:
                if block_delta_y > 0:
                    height = collided_object.rect.top - draw_y
                    self.drawing_moving_pos[1] = collided_object.rect.top
                    self.drawing_block.resize(width, height)
                    colliding_down = True
                if block_delta_y < 0:
                    self.drawing_moving_pos[1] = collided_object.rect.bottom
                    self.drawing_block.resize(width, height)
                    colliding_up = True

            self.adjust_drawing_block()


            # Apply motion
            change = mouse_x - self.drawing_moving_pos[0]
            print "change is", change, self.hspeed
            if colliding_right:
                if change < 0:
                    self.hspeed = change
            elif colliding_left:
                if change > 0:
                    self.hspeed = change
            else:
                self.hspeed = change

            change = mouse_y - self.drawing_moving_pos[1]
            if colliding_down:
                if change < 0:
                    self.vspeed = change
            elif colliding_up:
                if change > 0:
                    self.vspeed = change
            else:
                self.vspeed = change


        if event.type == pygame.MOUSEBUTTONDOWN:
            self.drawing_base_pos = mouse_pos
            self.drawing_moving_pos = [mouse_pos[0], mouse_pos[1]]
            self.drawing_block = SpriteFiller(Rect(mouse_pos, (0, 0)), ['data/blocks/snow.png', 'data/blocks/snow-filler.png'])
            if pygame.sprite.spritecollide(self.drawing_block, self.active_object_list, False):
                self.drawing_block = None

        if event.type == pygame.MOUSEBUTTONUP:
            if self.drawing_block:
                self.active_object_list.add(self.drawing_block)
            self.drawing_block = None

