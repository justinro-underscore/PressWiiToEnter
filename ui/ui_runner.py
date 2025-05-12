import pygame

class UIRunner:
    def __init__(self):
        # pygame setup
        pygame.init()

        # self.display = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self.display = pygame.display.set_mode((1720, 880))
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.player_pos = pygame.Vector2(self.display.get_width() / 2, self.display.get_height() / 2)

    def draw(self):
        # fill the screen with a color to wipe away anything from last frame
        self.display.fill('#525252')

        pygame.draw.circle(self.display, "red", self.player_pos, 40)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player_pos.y -= 300 * self.dt
        if keys[pygame.K_s]:
            self.player_pos.y += 300 * self.dt
        if keys[pygame.K_a]:
            self.player_pos.x -= 300 * self.dt
        if keys[pygame.K_d]:
            self.player_pos.x += 300 * self.dt

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        self.dt = self.clock.tick(60) / 1000

    def is_running(self):
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        # check for escape key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return False
        return True

    def quit(self):
        pygame.quit()
