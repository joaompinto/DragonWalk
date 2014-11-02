import pygame
from os import environ
from os.path import exists
from glob import glob
from pygame import Rect
from pygame.color import THECOLORS
from dragonwalk.gfx import ElasticSprite, SpriteFiller, AnimableSprite, ToolBox
from dragonwalk.player import Player, Level, PlayLoop
from dragonwalk.yattag import Doc, indent
from xml.dom import minidom


class TopWindow(object):

    def __init__(self, level_filename):

        environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.size = size = 1200, 1000
        self.frames_per_second = 60
        self.window = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.toolbox = toolbox = ToolBox(self.on_toolbox_change, (0, 0), (64, 64))
        self.active_object_list = pygame.sprite.Group()
        self.selected_tool_object = None   # Object selected at the toolbox
        self.player_object = None
        self.drawing_object = None  # Object currently being drawn
        self.selected_object = None
        self.hspeed = 0
        self.vspeed = 0
        self.is_mouse_down = False
        self.is_play_mode = False
        self.quit_requested = False
        self.font = pygame.font.SysFont("Times New Roman", 30)
        self.message = None
        self.level_filename = level_filename
        self.background = None

        self.set_background('data/backgrounds/sky1.png')

        for filename in glob('data/blocks/*.png')+glob('data/blocks/*.jpg'):
            if "-filler.png" in filename:
                continue
            image_list = [filename]
            filler_image = filename.split(".")[0]+"-filler.png"
            if exists(filler_image):
                image_list.append(filler_image)
            sprite = SpriteFiller((0, 0), (60, 60), image_list)
            toolbox.add(sprite)

        for filename in glob('data/objects/*.png'):
            if '_' in filename:  # State sprite
                continue
            file_name_list = [filename]
            base, ext = filename.split('.')
            walking_file = base+ '_walking.'+ext
            if exists(walking_file):
                file_name_list.append(walking_file)
            sprite = AnimableSprite((0, 0), (60, 60), file_name_list)
            toolbox.add(sprite)

    def set_background(self, filename):
        background = pygame.Surface(self.window.get_size())
        file_image = pygame.image.load(filename).convert()
        pygame.transform.smoothscale(file_image, (background.get_width(), background.get_height()), background)
        self.background = background

    def run_event_loop(self):

        while not self.quit_requested:
            if self.is_play_mode:
                self.run_play_loop()
            else:

                while self.handle_events():
                    self.draw(self.window)
                    self.clock.tick(self.frames_per_second)

        pygame.quit()

    def set_msg(self, text):
        self.message = self.font.render(text, True, THECOLORS['black'], THECOLORS['white'])

    def run_play_loop(self):
        self.is_play_mode = False
        if not self.player_object:
            return
        collide_object_list = pygame.sprite.Group()
        collect_object_list = pygame.sprite.Group()
        for obj in self.active_object_list:
            if obj == self.player_object:  # Do not collide/collect the player
                continue
            if isinstance(obj, AnimableSprite):
                if obj.collectable:
                    collect_object_list.add(obj)
                else:
                    collide_object_list.add(obj)
            else:
                collide_object_list.add(obj)
        player = Player(self.player_object.copy())
        player.position = self.player_object.position
        levels = [Level(self.window.get_size(), self.window, player, collide_object_list, collect_object_list)]
        playloop = PlayLoop(self.window, player, levels)
        playloop.run()

    def draw(self, surface):
        #self.window.fill(pygame.Color(200, 200, 200))
        surface.blit(self.background, (0, 0))
        self.active_object_list.draw(surface)
        if self.drawing_object:
            sprite = self.drawing_object.sprite
            #print "Drawing", sprite.position, sprite.size, sprite.image
            surface.blit(sprite.image, sprite.position)
            pygame.draw.rect(surface, THECOLORS['red'], sprite.rect, 1)
        if self.selected_object:
            rect = self.selected_object.rect
            pygame.draw.rect(surface, THECOLORS['green'], rect, 2)
            rect = Rect(rect.x+1, rect.y+1, rect.width-1, rect.height-1)
            pygame.draw.rect(surface, THECOLORS['black'], rect, 1)
        if self.player_object:
            rect = self.player_object.rect
            max_r = 10
            #max_r = min(rect.width, rect.height)/2
            pygame.draw.circle(surface, THECOLORS['white'], rect.center, max_r, 2)
            pygame.draw.circle(surface, THECOLORS['white'], rect.center, max_r-5, 2)

        self.toolbox.draw(surface)
        pygame.display.update()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
                return False
            if not self.handle_key_events(event):
                return False
            self.handle_mouse_events(event)
        return True

    def handle_key_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_play_mode = True
                return False

            if event.key == pygame.K_s:
                self.save()

            if event.key in [pygame.K_BACKSPACE, pygame.K_DELETE]:
                if self.selected_object:
                    self.active_object_list.remove(self.selected_object)
                    self.selected_object = None
                    if self.selected_object == self.player_object:
                        self.player_object = None

            if event.key == pygame.K_SPACE and self.selected_object:
                self.player_object = self.selected_object

        return True

    def move_unless_colliding(self):
        mouse_x, mouse_y = self.adjust_to_grid(pygame.mouse.get_pos())

        colliding_right = colliding_left = colliding_down = colliding_up = False

        # Apply horizontal speed and check for horizontal collisions
        self.drawing_object.moving_x += self.hspeed

        delta_x = self.drawing_object.moving_x - self.drawing_object.base_x
        collision_list = pygame.sprite.spritecollide(self.drawing_object.sprite, self.active_object_list, False)
        for collided_object in collision_list:
            if delta_x > 0:
                self.drawing_object.moving_x = collided_object.rect.left
                colliding_right = True
            if delta_x < 0:
                self.drawing_object.moving_x = collided_object.rect.right
                colliding_left = True

        # Apply vertical speed and check for vertical collisions
        self.drawing_object.moving_y += self.vspeed

        delta_y = self.drawing_object.moving_y - self.drawing_object.base_y
        collision_list = pygame.sprite.spritecollide(self.drawing_object.sprite, self.active_object_list, False)
        for collided_object in collision_list:
            if delta_y > 0: # Work-around for bug in an undetermined collision condition
                self.drawing_object.moving_y = collided_object.rect.top
                colliding_down = True
            if delta_y < 0:
                self.drawing_object.moving_y = collided_object.rect.bottom
                colliding_up = True

        # If colliding only move in the collision opposite direction
        change = mouse_x - self.drawing_object.moving_x
        if colliding_right:
            if change < 0:
                self.hspeed = change
        elif colliding_left:
            if change > 0:
                self.hspeed = change
        else:
            self.hspeed = change

        change = mouse_y - self.drawing_object.moving_y
        if colliding_down:
            if change < 0:
                self.vspeed = change
        elif colliding_up:
            if change > 0:
                self.vspeed = change
        else:
            self.vspeed = change

    def handle_mouse_events(self, event):

        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = self.adjust_to_grid(mouse_pos)

        if event.type == pygame.MOUSEMOTION:
            if self.is_mouse_down:
                if self.drawing_object:
                    self.move_unless_colliding()

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_mouse_down = True
            if self.toolbox.handle_events(event):
                return
            self.selected_object = None

            collision_list = [s for s in self.active_object_list.sprites() if s.rect.collidepoint(mouse_pos)]
            clicked_object = collision_list[0] if collision_list else None
            if clicked_object:
                if event.button == 3:
                    if clicked_object == self.selected_object:
                        self.selected_object = None
                    if clicked_object == self.player_object:
                        self.player_object = None
                    self.active_object_list.remove(clicked_object)
                else:
                    self.selected_object = clicked_object
            else:
                if self.selected_tool_object:
                    elastic_drawing_object = ElasticSprite(adjusted_mouse_pos, self.selected_tool_object.copy())
                    self.drawing_object = elastic_drawing_object

        if event.type == pygame.MOUSEBUTTONUP:
            self.is_mouse_down = False
            if self.drawing_object:
                if self.drawing_object.sprite.rect.width > 0 and self.drawing_object.sprite.rect.height > 0:
                    self.drawing_object.sprite.collectable = self.selected_tool_object.collectable
                    self.active_object_list.add(self.drawing_object.sprite)
            self.drawing_object = None

    def on_toolbox_change(self, sprite):
        self.selected_tool_object = sprite

    def adjust_to_grid(self, mouse_pos):
        GRID = 10.0
        x = mouse_pos[0]
        y = mouse_pos[1]
        x = round(x/GRID)*GRID
        y = round(y/GRID)*GRID
        return x, y

    def save(self):
        background_file_name = 'data/backgrounds/sky1.png'
        doc, tag, text = Doc().tagtext()
        with tag('level', size=','.join([str(x) for x in self.size])):
            with tag('background', filename=background_file_name): pass
            if self.player_object:
                with tag('player', position=','.join([str(x) for x in self.player_object.position])
                     , size=','.join([str(x) for x in self.player_object.size])
                    , image_list=','.join(self.player_object.image_filename_list)):
                    pass
            with tag('map'):
                for obj in self.active_object_list:
                    if obj == self.player_object:
                        continue
                    if isinstance(obj, SpriteFiller):
                        with tag('spritefiller', position=','.join([str(x) for x in obj.position])
                            , size=','.join([str(x) for x in obj.size])
                            , image_list=','.join(obj.image_filename_list)):
                            pass
                    if isinstance(obj, AnimableSprite):
                        with tag('animablesprite', position=','.join([str(x) for x in obj.position])
                            , size=','.join([str(x) for x in obj.size])
                            , image_list=','.join(obj.image_filename_list)
                            , is_collectable=str(obj.collectable)):
                            pass

        with open(self.level_filename, 'w') as save_file:
            save_file.write(indent(doc.getvalue()))

    def load(self):
        xmldoc = minidom.parse(self.level_filename)
        background = xmldoc.getElementsByTagName('background')[0]
        background_filename = background.attributes['filename'].value
        self.set_background(background_filename)
        player = xmldoc.getElementsByTagName('player')

        if player:
            player_info = player[0]
            position = [int(i) for i in player_info.attributes['position'].value.split(',')]
            size = [int(i) for i in player_info.attributes['size'].value.split(',')]
            image_list = player_info.attributes['image_list'].value.split(',')
            sprite = AnimableSprite(position, size,  image_list)
            self.active_object_list.add(sprite)
            self.player_object = sprite

        for sprite_info in xmldoc.getElementsByTagName('spritefiller'):
            position = [int(i) for i in sprite_info.attributes['position'].value.split(',')]
            size = [int(i) for i in sprite_info.attributes['size'].value.split(',')]
            image_list = sprite_info.attributes['image_list'].value.split(',')
            sprite = SpriteFiller(position, size, image_list)
            self.active_object_list.add(sprite)

        for sprite_info in xmldoc.getElementsByTagName('animablesprite'):
            position = [int(i) for i in sprite_info.attributes['position'].value.split(',')]
            size = [int(i) for i in sprite_info.attributes['size'].value.split(',')]
            image_list = sprite_info.attributes['image_list'].value.split(',')
            sprite = AnimableSprite(position, size,  image_list)
            sprite.collectable = (sprite_info.attributes['is_collectable'].value == 'True')
            self.active_object_list.add(sprite)



