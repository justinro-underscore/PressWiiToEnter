import pygame
from enum import Enum
from ui.screens.constants import Constants
from ui.screens.easings import ease_in_sine, ease_out_elastic
from ui.screens.screen import Screen, ScreenStates
from ui.screens.ui_object import UIObject


######################################################
#                    UI Objects                      #
######################################################


class UIObjCalibrationDialog(UIObject):
    def __init__(self, display_size, dialog_img):
        super().__init__()

        dialog_size = dialog_img.get_size()
        x_scale = (display_size[0] - (Constants.DIALOG_OFFSET * 2)) / dialog_size[0]
        y_scale = (display_size[1] - (Constants.DIALOG_OFFSET * 2)) / dialog_size[1]
        scale = min(x_scale, y_scale)
        dialog_size = (int(dialog_size[0] * scale), int(dialog_size[1] * scale))
        self.dialog_pos = ((display_size[0] - dialog_size[0]) / 2, (display_size[1] - dialog_size[1]) / 2)
        self.dialog_img = pygame.transform.scale(dialog_img, dialog_size)

    def update(self, dt, incoming_events, wm_state):
        return []

    def draw(self, display):
        display.blit(self.dialog_img, self.dialog_pos)



######################################################
#                      Screen                        #
######################################################


class CalibrationScreen(Screen):
    @property
    def screen_state(self):
        return ScreenStates.CALIBRATION_SCREEN

    @property
    def background_color(self):
        return '#525252'

    def __init__(self, display):
        super().__init__(display)
        display_size = display.get_size()
        dialog_img = pygame.image.load(Constants.DIALOG_IMG_FILE).convert_alpha()
        self.active_objs = [
            UIObjCalibrationDialog(display_size, dialog_img)
        ]