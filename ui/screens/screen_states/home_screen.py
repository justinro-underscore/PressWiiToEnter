import pygame
from enum import Enum
from ui.screens.constants import Constants
from ui.screens.screen import Screen, ScreenStates
from ui.screens.ui_object import UIObject

######################################################
#                      Screen                        #
######################################################


class HomeScreen(Screen):
    @property
    def screen_state(self):
        return ScreenStates.HOME_SCREEN

    @property
    def background_color(self):
        return '#ffffff'

    def __init__(self, display, init_events):
        super().__init__(display, init_events)
        display_size = display.get_size()
        self.active_objs = [
        ]