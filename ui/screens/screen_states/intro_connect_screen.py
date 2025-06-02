import pygame
from enum import Enum
from ui.screens.constants import Constants
from ui.screens.easings import ease_in_sine, ease_out_elastic
from ui.screens.screen import Screen, ScreenStates
from ui.screens.ui_object import UIObject


######################################################
#                    UI Objects                      #
######################################################


class UIObjIntroFade(UIObject):
    INIT_WAIT_LENGTH = 0.25
    FADE_LENGTH = 1.5

    def __init__(self, display_size, from_white_screen):
        super().__init__()
        self.surf = pygame.Surface(display_size)
        self.surf.fill('#525252' if not from_white_screen else '#ffffff')
        self.time = 0

    def update(self, dt, incoming_events, wm_state):
        self.time += dt
        if self.time >= self.INIT_WAIT_LENGTH:
            progress = min((self.time - self.INIT_WAIT_LENGTH) / self.FADE_LENGTH, 1)
            a = int(255 * (1 - ease_in_sine(progress)))
            self.surf.set_alpha(a)
            if progress >= 1:
                self.is_complete = True
                return [(UIObjConnectDialog, Constants.EVENT_FADED_IN)]
        return []

    def draw(self, display):
        display.blit(self.surf, (0,0))

######################################################

class ConnectDialogStates(Enum):
    WAITING_FOR_FADE = 1
    FADING_IN = 2
    IDLE = 3
    CONNECTED = 4
    FADING_OUT = 5

class UIObjConnectDialog(UIObject):
    FADE_IN_TIME = 0.5
    FADE_OUT_TIME = 1
    CONNECTED_BOUNCE_TIME = 0.75
    CONNECTED_TIME_OFFSET = 0.5

    def __init__(self, display_size, from_dialog):
        super().__init__()
        self.state = ConnectDialogStates.FADING_IN if from_dialog else ConnectDialogStates.WAITING_FOR_FADE

        dialog_img = pygame.image.load(Constants.DIALOG_IMG_FILE).convert_alpha()
        dialog_size = dialog_img.get_size()
        x_scale = (display_size[0] - (Constants.DIALOG_OFFSET * 2)) / dialog_size[0]
        y_scale = (display_size[1] - (Constants.DIALOG_OFFSET * 2)) / dialog_size[1]
        scale = min(x_scale, y_scale)
        dialog_size = (int(dialog_size[0] * scale), int(dialog_size[1] * scale))
        self.dialog_pos = ((display_size[0] - dialog_size[0]) / 2, (display_size[1] - dialog_size[1]) / 2)
        self.dialog_img = pygame.transform.scale(dialog_img, dialog_size)

        self.alpha = 0 if from_dialog else 255
        self.alpha_time = 0
        self.alpha_surf = pygame.Surface(dialog_size, pygame.SRCALPHA)
        self.alpha_surf.convert()

        press_connect_img = pygame.image.load('assets/images/intro-connecting/press-to-connect_upscaled.png').convert_alpha()
        press_connect_size = press_connect_img.get_size()
        press_connect_size = (int(press_connect_size[0] * scale * 0.25), int(press_connect_size[1] * scale * 0.25))
        press_connect_img_offset = (339, 41.5)
        self.press_connect_pos = (press_connect_img_offset[0] * scale, press_connect_img_offset[1] * scale)
        self.press_connect_img_orig = pygame.transform.scale(press_connect_img, press_connect_size)

        font_size = int(46 * scale)
        font = pygame.font.Font('assets/fonts/contb.ttf', font_size)
        self.text = font.render('Connect the Wiimote by pressing 1+2 on the remote.', True, '#444444')
        self.text_pos = self.text.get_rect(centerx=dialog_size[0] * 0.5, centery=dialog_size[1] * 0.7)

        self.connected_text = font.render('CONNECTED', True, '#4fbed1')
        self.connected_text_size = self.connected_text.get_size()
        self.connected_text_pos = self.connected_text.get_rect(centerx=dialog_size[0] * 0.5, centery=(dialog_size[1] * 0.7) + font_size)
        self.connected_text_scale_y = 0
        self.connected_time = 0

    def update(self, dt, incoming_events, wm_state):
        match self.state:
            case ConnectDialogStates.WAITING_FOR_FADE:
                if Constants.EVENT_FADED_IN in incoming_events:
                    self.state = ConnectDialogStates.IDLE
            case ConnectDialogStates.FADING_IN:
                self.alpha_time += dt
                self.alpha = min((self.alpha_time / self.FADE_IN_TIME) * 255, 255)
                if self.alpha == 255:
                    self.state = ConnectDialogStates.IDLE
            case ConnectDialogStates.IDLE:
                if wm_state.connected:
                    self.state = ConnectDialogStates.CONNECTED
            case ConnectDialogStates.CONNECTED:
                self.connected_time += dt
                if self.connected_time <= self.CONNECTED_BOUNCE_TIME:
                    self.connected_text_scale_y = ease_out_elastic(self.connected_time / self.CONNECTED_BOUNCE_TIME)
                    self.connected_text_copy = pygame.transform.scale(self.connected_text, (self.connected_text_size[0], self.connected_text_size[1] * self.connected_text_scale_y))
                else:
                    if self.connected_text_scale_y != 1:
                        self.connected_text_scale_y = 1
                        self.connected_text = pygame.transform.scale(self.connected_text, self.connected_text_size)
                    if self.connected_time >= self.CONNECTED_BOUNCE_TIME + self.CONNECTED_TIME_OFFSET:
                        self.state = ConnectDialogStates.FADING_OUT
            case ConnectDialogStates.FADING_OUT:
                self.alpha_time += dt
                self.alpha = max(((self.FADE_OUT_TIME - self.alpha_time) / self.FADE_OUT_TIME) * 255, 0)
                if self.alpha == 0:
                    return ScreenStates.CALIBRATION_SCREEN
        return []

    def draw(self, display):
        display.blit(self.dialog_img, self.dialog_pos)

        if self.alpha >= 0:
            self.alpha_surf.fill((0, 0, 0, 0))
            self.alpha_surf.blit(self.press_connect_img_orig, self.press_connect_pos)
            self.alpha_surf.blit(self.text, self.text_pos)
            if self.connected_text_scale_y > 0:
                self.alpha_surf.blit(self.connected_text_copy, self.connected_text_pos)
            temp_surf = self.alpha_surf.copy()
            temp_surf.set_alpha(self.alpha)
            display.blit(temp_surf, self.dialog_pos)



######################################################
#                      Screen                        #
######################################################


class IntroConnectScreen(Screen):
    @property
    def screen_state(self):
        return ScreenStates.INTRO_CONNECT_SCREEN

    @property
    def background_color(self):
        return '#525252'

    def __init__(self, display, init_events):
        super().__init__(display, init_events)

        from_dialog = Constants.EVENT_FROM_DIALOG in init_events
        from_white_screen = Constants.EVENT_FROM_WHITE_SCREEN in init_events
        self.active_objs = [
            UIObjConnectDialog(self.display_size, from_dialog),
        ]
        if not from_dialog:
            self.active_objs += [UIObjIntroFade(self.display_size, from_white_screen)]