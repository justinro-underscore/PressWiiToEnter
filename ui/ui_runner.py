import pygame
from collections.abc import Sequence
from random import random
from ui.screens.constants import Constants
from ui.screens.screen import ScreenStates
from ui.screens.screen_states.intro_connect_screen import IntroConnectScreen
from ui.screens.screen_states.intro_pickup_screen import IntroPickupScreen
from ui.screens.screen_states.calibration_screen import CalibrationScreen
from ui.screens.screen_states.home_screen import HomeScreen

class UIRunner:
    SCREEN_STATES = {
        ScreenStates.INTRO_CONNECT_SCREEN: IntroConnectScreen,
        ScreenStates.INTRO_PICKUP_SCREEN: IntroPickupScreen,
        ScreenStates.CALIBRATION_SCREEN: CalibrationScreen,
        ScreenStates.HOME_SCREEN: HomeScreen
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
        self.pygame_events = []

        # self.wm_acc_test = [150, 0, 75]
        # self.increasing = [False, False, False]
        # self.increasing_time = [0, 0, 0]
        # self.wm_acc_test_enabled = True

        self.curr_screen = self.SCREEN_STATES[ScreenStates.HOME_SCREEN](self.display, [])

    def update(self, wm_state):
        pygame_events = []
        for event in self.pygame_events:
            if event.type == pygame.KEYDOWN:
                pygame_events += [Constants.EVENT_KEYDOWN + str(event.key)]
                # if event.key == pygame.K_q:
                #     if not self.wm_acc_test_enabled:
                #         wm_state.connected = False
                #     else:
                #         self.wm_acc_test_enabled = False

        # if self.wm_acc_test_enabled:
        #     for i in range(len(self.wm_acc_test)):
        #         if self.increasing_time[i] <= 0:
        #             self.increasing[i] = random() < 0.5
        #             self.increasing_time[i] = random() * 1
        #         self.wm_acc_test[i] += self.dt * (1 if self.increasing[i] else -1) * 20
        #         self.wm_acc_test[i] = max(min(self.wm_acc_test[i], 255), 0)
        #         self.increasing_time[i] -= self.dt
        #     new_state = (int(self.wm_acc_test[0]), int(self.wm_acc_test[1]), int(self.wm_acc_test[2]))
        #     wm_state.acc = new_state
        # print(wm_state.acc)

        new_screen = self.curr_screen.update(self.dt, pygame_events, wm_state)

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
            events = []
            if not isinstance(new_screen, str) and isinstance(new_screen, Sequence):
                if not isinstance(new_screen[1], str) and isinstance(new_screen[1], Sequence):
                    events = new_screen[1]
                else:
                    events = [new_screen[1]]
                new_screen = new_screen[0]
            self.curr_screen = self.SCREEN_STATES[new_screen](self.display, events)

    def is_running(self):
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        self.pygame_events = pygame.event.get()
        for event in self.pygame_events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

        return True

    def quit(self):
        pygame.quit()
