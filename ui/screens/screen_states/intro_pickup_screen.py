import pygame
from enum import Enum
from ui.screens.constants import Constants
from math import sin
from ui.screens.screen import Screen, ScreenStates
from ui.screens.ui_object import UIObject


######################################################
#                    UI Objects                      #
######################################################

class PickUpDialogStates(Enum):
    FADING_IN = 1
    IDLE = 2,
    FADING_OUT = 3

class UIObjPickUpDialog(UIObject):
    FADE_IN_TIME = 1.5
    FADE_OUT_TIME = 0.6
    TEXT_MOVE_FREQ = 4
    TEXT_MOVE_AMOUNT = 3

    def __init__(self, display_size, dialog_img, pick_up_img):
        super().__init__()
        self.state = PickUpDialogStates.FADING_IN

        self.dialog_size = dialog_img.get_size()
        x_scale = (display_size[0] - (Constants.DIALOG_OFFSET * 2)) / self.dialog_size[0]
        y_scale = (display_size[1] - (Constants.DIALOG_OFFSET * 2)) / self.dialog_size[1]
        scale = min(x_scale, y_scale)
        self.dialog_size = (int(self.dialog_size[0] * scale), int(self.dialog_size[1] * scale))
        self.dialog_pos = ((display_size[0] - self.dialog_size[0]) / 2, (display_size[1] - self.dialog_size[1]) / 2)
        self.dialog_img = pygame.transform.scale(dialog_img, self.dialog_size)

        self.alpha = 0
        self.alpha_time = 0
        self.alpha_surf = pygame.Surface(self.dialog_size, pygame.SRCALPHA)
        self.alpha_surf.convert()

        pick_up_size = pick_up_img.get_size()
        pick_up_size = (int(pick_up_size[0] * scale * 0.75), int(pick_up_size[1] * scale * 0.75))
        pick_up_img_offset = (335, 42)
        self.pick_up_pos = (pick_up_img_offset[0] * scale, pick_up_img_offset[1] * scale)
        self.pick_up_img_orig = pygame.transform.scale(pick_up_img, pick_up_size)

        font = pygame.font.Font('assets/fonts/contb.ttf', 72)
        self.text_time = 0
        self.text = font.render('Pick up the Wii remote', True, '#444444')
        self.text_size = self.text.get_size()
        self.text_pos_orig = self.text.get_rect(centerx=self.dialog_size[0] * 0.5, centery=self.dialog_size[1] * 0.72)
        self.text_pos = self.text_pos_orig

    def update(self, dt, incoming_events, wm_state):
        self.text_time += dt
        offset = sin(self.text_time * self.TEXT_MOVE_FREQ) * self.TEXT_MOVE_AMOUNT
        self.text_pos = (self.text_pos_orig[0], self.text_pos_orig[1] + offset)

        match self.state:
            case PickUpDialogStates.FADING_IN:
                self.alpha_time += dt
                self.alpha = min((self.alpha_time / self.FADE_IN_TIME) * 255, 255)
                if self.alpha == 255:
                    self.alpha_time = 0
                    self.state = PickUpDialogStates.FADING_OUT
            case PickUpDialogStates.IDLE:
                pass
            case PickUpDialogStates.FADING_OUT:
                self.alpha_time += dt
                self.alpha = max(((self.FADE_OUT_TIME - self.alpha_time) / self.FADE_OUT_TIME) * 255, 0)
                if self.alpha == 0:
                    return ScreenStates.CALIBRATION_SCREEN
        return []

    def draw(self, display):
        display.blit(self.dialog_img, self.dialog_pos)

        if self.alpha >= 0:
            self.alpha_surf.fill((0, 0, 0, 0))
            self.alpha_surf.blit(self.pick_up_img_orig, self.pick_up_pos)
            self.alpha_surf.blit(self.text, self.text_pos)
            temp_surf = self.alpha_surf.copy()
            temp_surf.set_alpha(self.alpha)
            display.blit(temp_surf, self.dialog_pos)



######################################################
#                      Screen                        #
######################################################


class IntroPickupScreen(Screen):
    @property
    def screen_state(self):
        return ScreenStates.INTRO_PICKUP_SCREEN

    @property
    def background_color(self):
        return '#525252'

    def __init__(self, display):
        super().__init__(display)
        display_size = display.get_size()
        dialog_img = pygame.image.load(Constants.DIALOG_IMG_FILE).convert_alpha()
        pickup_img = pygame.image.load('assets/images/pick-up-remote_upscaled.png').convert_alpha()
        self.active_objs = [
            UIObjPickUpDialog(display_size, dialog_img, pickup_img)
        ]