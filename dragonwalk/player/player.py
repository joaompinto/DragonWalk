import pygame

RIGHT = 1
LEFT = 2

class Player(pygame.sprite.Sprite):

    def __init__(self, image):
        super(Player, self).__init__()
        self.image = image
        self.set_properties()
        self.hspeed = 0
        self.face_direction = RIGHT
        self.vspeed = 0
        self._level = None

    @property
    def position(self):
        return self.rect.x, self.rect.y

    @position.setter
    def position(self, value):
        self.rect.x, self.rect.y = value

    def set_properties(self):
        self.rect = self.image.get_rect()
        self.speed = 5

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level

    def set_image(self, filename=None):
        file_image = pygame.image.load(filename).convert_alpha()
        pygame.transform.scale(file_image, (self.rect.width, self.rect.height), self.image)
        self.set_properties()

    def update(self, collidable=pygame.sprite.Group(), event=None):

        hitting_the_ground_boundary = False
        self.experience_gravity()

        self.rect.x += self.hspeed

        # Check horizontal collisions
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if self.hspeed > 0:
                self.rect.right = collided_object.rect.left
            if self.hspeed < 0:
                self.rect.left = collided_object.rect.right

        self.rect.y += self.vspeed

        # Check level boundaries
        if self.rect.bottom > self.level.size[1]:
            self.position = self.position[0], self.level.size[1] - self.rect.height
            #self.rect.bottom = self.level.size[1]
            if self.vspeed > 0:
                hitting_the_ground_boundary = True
                self.vspeed = 0

        # Check vertical collisions
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if self.vspeed > 0:
                self.rect.bottom = collided_object.rect.top
                self.vspeed = 0
            if self.vspeed < 0:
                self.rect.top = collided_object.rect.bottom
                self.vspeed = 0

        if event:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.hspeed = -self.speed
                if event.key == pygame.K_RIGHT:
                    self.hspeed = self.speed
                if event.key in [pygame.K_UP, pygame.K_SPACE]:
                    if hitting_the_ground_boundary or len(collision_list) > 0:  # Only jump when hitting in the ground
                        self.vspeed = -self.speed*2

            if event.type == pygame.KEYUP:  # Reset current speed
                if event.key == pygame.K_LEFT:
                    if self.hspeed < 0:
                        self.hspeed = 0
                if event.key == pygame.K_RIGHT:
                    if self.hspeed > 0:
                        self.hspeed = 0

        if self.face_direction == RIGHT and self.hspeed < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.face_direction = LEFT
        if self.face_direction == LEFT and self.hspeed > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.face_direction = RIGHT

    def experience_gravity(self, gravity=.35):
        if self.vspeed == 0:  # Keep applying gravity
            self.vspeed = 1
        else:
            self.vspeed += gravity

    def draw(self, surface):
        surface.blit(self.image, self.rect)