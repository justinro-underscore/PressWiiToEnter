import pygame
from ui.screens.screen import ScreenStates
from ui.screens.screen_states.intro_connect_screen import IntroConnectScreen
from ui.screens.screen_states.intro_pickup_screen import IntroPickupScreen
from ui.screens.screen_states.calibration_screen import CalibrationScreen

class UIRunner:
    SCREEN_STATES = {
        ScreenStates.INTRO_CONNECT_SCREEN: IntroConnectScreen,
        ScreenStates.INTRO_PICKUP_SCREEN: IntroPickupScreen,
        ScreenStates.CALIBRATION_SCREEN: CalibrationScreen
    }

    def __init__(self):
        # pygame setup
        pygame.init()

        # self.display = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self.display = pygame.display.set_mode((1720, 880))
        pygame.display.set_caption('Press Wii to Enter')
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.dt = 0

        self.curr_screen = self.SCREEN_STATES[ScreenStates.INTRO_PICKUP_SCREEN](self.display)

    def update(self, wm_state):
        new_screen = self.curr_screen.update(self.dt, wm_state)

        self.display.fill(self.curr_screen.background_color)
        self.curr_screen.draw()

        self.curr_screen.clean()

        # flip() the display to put your work on screen
        # pygame.display.flip()
        pygame.display.update()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        self.dt = self.clock.tick(60) / 1000

        if new_screen is not None:
            self.curr_screen = self.SCREEN_STATES[new_screen](self.display)

    def is_running(self):
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

        return True

    def quit(self):
        pygame.quit()
