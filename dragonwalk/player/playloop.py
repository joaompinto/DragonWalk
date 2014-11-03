import pygame
from dragonwalk.gfx import TextBox

class PlayLoop(object):

    def __init__(self, window, level):
        self.window = window
        self.player = level.player_object
        self.current_level_number = 0
        self.current_level = level

        self.text = TextBox((100, 100))

    def run(self):
        window = self.window
        frames_per_second = 60
        current_level = self.current_level
        player = self.player
        clock = pygame.time.Clock()
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
            current_level.update()

            # Logic Testing
            current_level.run_viewbox()
            if current_level.clear_collected(player):
                self.text.text = "Level Completed!"

            # Draw everything
            current_level.draw(window)
            player.draw(window)

            self.text.draw(window)

            # Delay Framerate
            clock.tick(frames_per_second)

            # Update the screen
            pygame.display.update()