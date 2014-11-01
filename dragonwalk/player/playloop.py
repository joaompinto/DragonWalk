import pygame

class PlayLoop(object):

    def __init__(self, player, level_list):
        self.player = player
        self.current_level_number = 0
        self.current_level = level_list[self.current_level_number]

    def run(self, window):
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
            event = None

            current_level.update()

            # Logic Testing
            current_level.run_viewbox()
            current_level.clear_collected(player)

            # Draw everything
            current_level.draw(window)
            player.draw(window)

            # Delay Framerate
            clock.tick(frames_per_second)

            # Update the screen
            pygame.display.update()