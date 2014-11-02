import pygame

class Level(object):

    def __init__(self, size, window, player_object, collide_object_list=pygame.sprite.Group(), collect_object_list=pygame.sprite.Group()):
        window_width, window_height = window.get_width(), window.get_height()
        self.size = size
        self.window_width, self.window_height = window_width, window_height
        self.player_object = player_object
        self.world_shift_x = self.world_shift_y = 0
        self.left_viewbox = window_width/2 - window_width/8
        self.right_viewbox = window_width/2 + window_width/10
        self.up_viewbox = window_height/5
        self.down_viewbox = window_height/2
        self.collide_object_list = collide_object_list
        self.collect_object_list = collect_object_list
        player_object.level = self

        background = pygame.Surface(window.get_size())
        file_image = pygame.image.load('data/backgrounds/sky1.png').convert()
        pygame.transform.smoothscale(file_image, (background.get_width(), background.get_height()), background)
        self.background = background

    def update(self):
        self.collide_object_list.update()
        self.collect_object_list.update()

    def draw(self, window):
        window.blit(self.background, (0, 0))
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
        window_width, window_height = self.window_width, self.window_height


        # Scroll left ?
        if self.player_object.rect.x <= self.left_viewbox:
            if self.world_shift_x < 0:  # Not at the left edge
                view_difference = self.left_viewbox - self.player_object.rect.x
                self.player_object.rect.x = self.left_viewbox  # Stop the player movement
                self.shift_world(view_difference, 0)

        if self.player_object.rect.x >= self.right_viewbox:
            if abs(self.world_shift_x)+window_width < self.size[0]:  # Not at the right edge
                view_difference = self.right_viewbox - self.player_object.rect.x
                self.player_object.rect.x = self.right_viewbox  # Stop the player movement
                # Don't allow view_difference to scroll over the right edge
                if abs(self.world_shift_x+view_difference) > self.size[0]-window_width:
                    view_difference = -(self.size[0]-window_width-abs(self.world_shift_x))
                self.shift_world(view_difference, 0)

        # Check if needs to scroll up
        if self.player_object.rect.y <= self.up_viewbox:
            if self.world_shift_y < 0:  # Not at the top edge
                view_difference = self.up_viewbox - self.player_object.rect.y
                self.player_object.rect.y = self.up_viewbox  # Stop the player movement
                self.shift_world(0, view_difference)

        if self.player_object.rect.y >= self.down_viewbox:
            if abs(self.world_shift_y)+window_height < self.size[1]:  # Not at the bottom edge:
                view_difference = self.down_viewbox - self.player_object.rect.y
                self.player_object.rect.y = self.down_viewbox  # Stop the player movement
                #  Don't allow view_difference to scroll below the bottom edge
                if abs(self.world_shift_y+view_difference) > self.size[1]-window_height:
                    view_difference = -(self.size[1]-window_height-abs(self.world_shift_y))
                self.shift_world(0, view_difference)


    def clear_collected(self, player):
        collection_list = pygame.sprite.spritecollide(self.player_object, self.collect_object_list, False)
        for obj in collection_list:
            self.collect_object_list.remove(obj)
        return len(self.collect_object_list) == 0