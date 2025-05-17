import pygame
from ui.screens.easings import ease_in_sine
from ui.screens.screen import Screen, ScreenStates
from ui.screens.ui_object import UIObject


######################################################
#                    UI Objects                      #
######################################################


class UIObjIntroFade(UIObject):
    INIT_WAIT_LENGTH = 0.25
    FADE_LENGTH = 1.5

    def __init__(self, display_size):
        super().__init__()
        self.surf = pygame.Surface(display_size)
        self.surf.fill('#525252')
        self.time = 0

    def update(self, dt, incoming_events):
        self.time += dt
        if self.time >= self.INIT_WAIT_LENGTH:
            progress = min((self.time - self.INIT_WAIT_LENGTH) / self.FADE_LENGTH, 1)
            a = int(255 * (1 - ease_in_sine(progress)))
            self.surf.set_alpha(a)
            if progress >= 1:
                self.is_complete = True
        return []

    def draw(self, display):
        display.blit(self.surf, (0,0))

######################################################

class UIObjConnectDialog(UIObject):
    DIALOG_OFFSET = 50

    def __init__(self, display_size, dialog_img, press_connect_img):
        super().__init__()
        dialog_size = dialog_img.get_size()
        x_scale = (display_size[0] - (self.DIALOG_OFFSET * 2)) / dialog_size[0]
        y_scale = (display_size[1] - (self.DIALOG_OFFSET * 2)) / dialog_size[1]
        scale = min(x_scale, y_scale)
        dialog_size = (int(dialog_size[0] * scale), int(dialog_size[1] * scale))
        self.dialog_pos = ((display_size[0] - dialog_size[0]) / 2, (display_size[1] - dialog_size[1]) / 2)
        self.dialog_img = pygame.transform.scale(dialog_img, dialog_size)

        press_connect_size = press_connect_img.get_size()
        press_connect_size = (int(press_connect_size[0] * scale), int(press_connect_size[1] * scale))
        press_connect_img_offset = (339, 41.5)
        self.press_connect_pos = (self.dialog_pos[0] + (press_connect_img_offset[0] * scale), self.dialog_pos[1] + (press_connect_img_offset[1] * scale))
        self.press_connect_img_orig = pygame.transform.scale(press_connect_img, press_connect_size)

        font = pygame.font.Font('assets/fonts/contb.ttf', 54)
        text_orig = font.render('Connect the Wiimote by pressing 1+2 on the remote.', True, '#444444')
        self.text = text_orig.copy()
        text_size = self.text.get_size()
        self.text_pos = ((dialog_size[0] * 0.5) + self.dialog_pos[0] - (text_size[0] * 0.5), (dialog_size[1] * 0.7) + self.dialog_pos[1])
        self.text_surface = pygame.Surface(text_size, pygame.SRCALPHA)

    def draw(self, display):
        display.blit(self.dialog_img, self.dialog_pos)

        display.blit(self.press_connect_img_orig, self.press_connect_pos)

        self.text_surface.fill((255, 255, 255, 255))
        self.text.blit(self.text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        display.blit(self.text, self.text_pos)



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

    def __init__(self, display):
        super().__init__(display)
        display_size = display.get_size()
        dialog_img = pygame.image.load('assets/images/dialog.png').convert_alpha()
        press_connect_img = pygame.image.load('assets/images/press-to-connect.png').convert_alpha()
        self.active_objs = [
            UIObjConnectDialog(display_size, dialog_img, press_connect_img),
            UIObjIntroFade(display_size)
        ]