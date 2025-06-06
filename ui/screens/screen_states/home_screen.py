import pygame
import cv2
from enum import Enum
from math import cos
from ui.screens.constants import Constants
from ui.screens.easings import ease_in_sine, ease_out_sine
from ui.screens.screen import Screen, ScreenStates
from ui.screens.ui_object import UIObject



######################################################
#                    UI Objects                      #
######################################################


class UIObjIntroFade(UIObject):
    INIT_WAIT_LENGTH = 0.5
    FADE_LENGTH = 1.5

    def __init__(self, display_size):
        super().__init__()
        self.surf = pygame.Surface(display_size)
        self.surf.fill('#ffffff')
        self.time = 0

    def update(self, dt, incoming_events, wm_state):
        self.time += dt
        if self.time >= self.INIT_WAIT_LENGTH:
            progress = min((self.time - self.INIT_WAIT_LENGTH) / self.FADE_LENGTH, 1)
            a = int(255 * (1 - ease_in_sine(progress)))
            self.surf.set_alpha(a)
            if progress >= 1:
                self.is_complete = True
                return [(UIObjTitle, Constants.EVENT_FADED_IN)]
        return []

    def draw(self, display):
        display.blit(self.surf, (0,0))

######################################################

class UIObjDisconnectedFadeOut(UIObject):
    FADE_LENGTH = 0.5

    def __init__(self, display_size):
        super().__init__()
        self.surf = pygame.Surface(display_size)
        self.surf.fill('#ffffff')
        self.surf.set_alpha(0)
        self.fading = False
        self.time = 0

    def update(self, dt, incoming_events, wm_state):
        if self.fading:
            self.time += dt
            progress = min(self.time / self.FADE_LENGTH, 1)
            a = int(255 * ease_out_sine(progress))
            self.surf.set_alpha(a)
            if progress >= 1:
                return (ScreenStates.INTRO_CONNECT_SCREEN, Constants.EVENT_FROM_WHITE_SCREEN)
        elif Constants.EVENT_WIIMOTE_DISCONNECTED in incoming_events:
            self.fading = True
        return []

    def draw(self, display):
        display.blit(self.surf, (0,0))

######################################################

class UIObjWelcomeInStates(Enum):
    WAITING_FOR_ACTIVATION = 1
    FADING_IN = 2
    PAUSING = 3
    FADE_AWAY = 4

class UIObjWelcomeIn(UIObject):
    FADE_IN_LENGTH = 1.5
    FADE_IN_ALPHA_MAX = 200

    MIN_PAUSE_TIME = 4
    PAUSE_ROT_THRESHOLD = 3
    PAUSE_ROT_TIME = 2

    FADE_AWAY_LENGTH = 2

    def __init__(self, display_size):
        super().__init__()
        self.state = UIObjWelcomeInStates.WAITING_FOR_ACTIVATION

        self.fade_surf = pygame.Surface(display_size).convert_alpha()
        self.fade_surf.fill('#000000')
        self.fade_surf.set_alpha(0)

        font1 = pygame.font.Font('assets/fonts/contb.ttf', 104)
        self.text1 = font1.render('WELCOME TO WUHU ISLAND!', True, '#ffffff').convert_alpha()
        self.text1_pos = self.text1.get_rect(centerx=display_size[0] * 0.5, bottom=display_size[1] * 0.5 - 5)
        font2 = pygame.font.Font('assets/fonts/contb.ttf', 48)
        self.text2 = font2.render('Please leave the Wii Remote on the table', True, '#ffffff').convert_alpha()
        self.text2_pos = self.text2.get_rect(centerx=display_size[0] * 0.5, top=display_size[1] * 0.5 + 5)
        self.text_surf = pygame.Surface(display_size, pygame.SRCALPHA).convert_alpha()
        self.text_surf.blit(self.text1, self.text1_pos)
        self.text_surf.blit(self.text2, self.text2_pos)
        self.text_surf.set_alpha(0)

        self.time = 0

        self.last_wm_acc = None
        self.acc_check_time = 0

    def update(self, dt, incoming_events, wm_state):
        match self.state:
            case UIObjWelcomeInStates.WAITING_FOR_ACTIVATION:
                if Constants.EVENT_HOME_READY in incoming_events:
                    self.state = UIObjWelcomeInStates.FADING_IN
            case UIObjWelcomeInStates.FADING_IN:
                self.time += dt
                progress = min(self.time / self.FADE_IN_LENGTH, 1)
                x = ease_in_sine(progress)
                self.fade_surf.set_alpha(int(self.FADE_IN_ALPHA_MAX * x))
                self.text_surf.set_alpha(int(255 * x))
                if progress >= 1:
                    self.time = 0
                    self.state = UIObjWelcomeInStates.PAUSING
            case UIObjWelcomeInStates.PAUSING:
                self.time += dt

                ready = False
                if wm_state.connected:
                    rot_delta = 0
                    if self.last_wm_acc is not None:
                        for i in range(len(wm_state.acc)):
                            rot_delta += abs(wm_state.acc[i] - self.last_wm_acc[i])
                    self.last_wm_acc = wm_state.acc

                    if rot_delta < self.PAUSE_ROT_THRESHOLD:
                        self.acc_check_time += dt
                        if self.acc_check_time >= self.PAUSE_ROT_TIME:
                            ready = True
                    else:
                        self.acc_check_time = 0
                else:
                    ready = True

                if self.time >= self.MIN_PAUSE_TIME and ready:
                    self.time = 0
                    self.state = UIObjWelcomeInStates.FADE_AWAY
            case UIObjWelcomeInStates.FADE_AWAY:
                self.time += dt
                progress = min(self.time / self.FADE_AWAY_LENGTH, 1)
                x = ease_out_sine(progress)
                self.fade_surf.set_alpha(int((255 - self.FADE_IN_ALPHA_MAX) * x + self.FADE_IN_ALPHA_MAX))
                self.text_surf.set_alpha(int(255 * (1 - x)))
                if progress >= 1:
                    if wm_state.connected:
                        return (ScreenStates.INTRO_PICKUP_SCREEN, Constants.EVENT_FROM_BLACK_SCREEN)
                    else:
                        return (ScreenStates.INTRO_CONNECT_SCREEN, Constants.EVENT_FROM_BLACK_SCREEN)
        return []

    def draw(self, display):
        if self.state == UIObjWelcomeInStates.WAITING_FOR_ACTIVATION:
            return
        display.blit(self.fade_surf, (0,0))
        display.blit(self.text_surf, (0,0))

######################################################

class UIObjTitleStates(Enum):
    WAITING_FOR_FADE = 1
    SWOOPING_IN = 2
    IDLE = 3
    FADING_OUT = 4

class UIObjTitle(UIObject):
    MOVE_TIME = 1.5

    PRESS_BTN_MOVE_SCALAR = 6
    PRESS_BTN_MOVE = 4
    PRESS_BTN_POP_TIME = 0.15
    PRESS_BTN_POP_SCALE_TO = 0.5

    BTN_FADE_TIME = 0.1
    BTN_BALLOON_POP_TIME = 0.15
    BTN_BALLOON_POP_SCALAR = 0.3

    READY_TIME = 0.1

    FADE_OUT_TIME = 0.5

    def __init__(self, display_size):
        super().__init__()
        self.state = UIObjTitleStates.WAITING_FOR_FADE

        title_img = pygame.image.load('assets/images/home/wii-sports-resort-title.png').convert_alpha()
        title_size = title_img.get_size()
        scale = display_size[0] / title_size[0]
        title_size = (int(title_size[0] * scale), int(title_size[1] * scale))

        self.alpha = 0
        self.alpha_surf = pygame.Surface(title_size, pygame.SRCALPHA).convert_alpha()
        self.title_img = pygame.transform.scale(title_img, title_size)
        self.title_start_pos = display_size[0]
        self.title_pos = self.alpha_surf.get_rect(left=display_size[0], bottom=display_size[1])

        self.swoop_time = 0
        self.fade_out_time = 0

        press_btns_img = pygame.image.load('assets/images/home/press-a-and-b.png').convert_alpha()
        press_btns_size = press_btns_img.get_size()
        self.press_btns_orig_size = (press_btns_size[0] * scale, press_btns_size[1] * scale)
        self.press_btns_orig_img = pygame.transform.scale(press_btns_img, self.press_btns_orig_size)
        self.press_btns_img = self.press_btns_orig_img.copy()
        self.press_btns_anchor = (424 * scale, (276 * scale) + self.press_btns_orig_size[1]) # (Left, Bottom)
        self.press_btns_y_offset = 0
        self.press_btns_y_max_offset = self.PRESS_BTN_MOVE * scale
        self.press_btns_move_time = 0
        self.press_btns_pop_time = 0

        a_img = pygame.image.load('assets/images/home/a-overlay.png').convert_alpha()
        self.a_alpha_surf = pygame.Surface(title_size, pygame.SRCALPHA).convert_alpha()
        self.a_alpha_surf.blit(pygame.transform.scale(a_img, title_size), (0,0))
        self.a_alpha_surf.set_alpha(0)
        self.a_alpha = 0
        self.a_pressed = False
        self.a_alpha_time = self.BTN_FADE_TIME

        a_balloon = pygame.image.load('assets/images/home/a-balloon.png').convert_alpha()
        a_balloon_invert = pygame.image.load('assets/images/home/a-balloon-invert.png').convert_alpha()
        a_balloon_size = a_balloon.get_size()
        self.a_balloon_orig_size = (a_balloon_size[0] * scale, a_balloon_size[1] * scale)
        self.a_balloon = pygame.transform.scale(a_balloon, self.a_balloon_orig_size)
        self.a_balloon_invert_orig = pygame.transform.scale(a_balloon_invert, self.a_balloon_orig_size)
        self.a_balloon_invert = self.a_balloon_invert_orig.copy()
        self.a_balloon_anchor = (1404 * scale, 258 * scale)
        self.a_balloon_pos = self.a_balloon.get_rect(centerx=self.a_balloon_anchor[0], bottom=self.a_balloon_anchor[1])
        self.a_balloon_invert_pos = (self.a_balloon_pos[0], self.a_balloon_pos[1])
        self.a_balloon_pop_time = 0

        b_img = pygame.image.load('assets/images/home/b-overlay.png').convert_alpha()
        self.b_alpha_surf = pygame.Surface(title_size, pygame.SRCALPHA).convert_alpha()
        self.b_alpha_surf.blit(pygame.transform.scale(b_img, title_size), (0,0))
        self.b_alpha_surf.set_alpha(0)
        self.b_alpha = 0
        self.b_pressed = False
        self.b_alpha_time = self.BTN_FADE_TIME

        b_balloon = pygame.image.load('assets/images/home/b-balloon.png').convert_alpha()
        b_balloon_invert = pygame.image.load('assets/images/home/b-balloon-invert.png').convert_alpha()
        b_balloon_size = b_balloon.get_size()
        self.b_balloon_orig_size = (b_balloon_size[0] * scale, b_balloon_size[1] * scale)
        self.b_balloon = pygame.transform.scale(b_balloon, self.b_balloon_orig_size)
        self.b_balloon_invert_orig = pygame.transform.scale(b_balloon_invert, self.b_balloon_orig_size)
        self.b_balloon_invert = self.b_balloon_invert_orig.copy()
        self.b_balloon_anchor = (1394 * scale, 316 * scale)
        self.b_balloon_pos = self.b_balloon.get_rect(right=self.b_balloon_anchor[0], top=self.b_balloon_anchor[1])
        self.b_balloon_invert_pos = (self.b_balloon_pos[0], self.b_balloon_pos[1])
        self.b_balloon_pop_time = 0

        self.ready_time = 0

    def update(self, dt, incoming_events, wm_state):
        if self.state != UIObjTitleStates.WAITING_FOR_FADE:
            self.press_btns_move_time += dt
            self.press_btns_y_offset = cos(self.press_btns_move_time * self.PRESS_BTN_MOVE_SCALAR) * self.press_btns_y_max_offset

        match self.state:
            case UIObjTitleStates.WAITING_FOR_FADE:
                if Constants.EVENT_FADED_IN in incoming_events:
                    self.state = UIObjTitleStates.SWOOPING_IN
            case UIObjTitleStates.SWOOPING_IN:
                self.swoop_time += dt
                x = self.swoop_time / self.MOVE_TIME
                self.alpha = ease_in_sine(x) * 255
                new_pos_x = (1 - ease_out_sine(x)) * self.title_start_pos
                self.title_pos = (new_pos_x, self.title_pos[1])
                if x >= 1:
                    self.state = UIObjTitleStates.IDLE
            case UIObjTitleStates.IDLE:
                if not wm_state.connected:
                    return [(UIObjDisconnectedFadeOut, Constants.EVENT_WIIMOTE_DISCONNECTED)]

                if (not self.a_pressed and wm_state.a_btn) or (self.a_pressed and not wm_state.a_btn):
                    self.a_alpha_time = 0
                    self.a_pressed = wm_state.a_btn
                    self.a_balloon_pop_time = 0
                if self.a_alpha_time < self.BTN_FADE_TIME:
                    self.a_alpha_time += dt
                    x = min(self.a_alpha_time / self.BTN_FADE_TIME, 1)
                    alpha = (x if self.a_pressed else (1 - x)) * 255
                    self.a_alpha_surf.set_alpha(alpha)
                if self.a_pressed and self.a_balloon_pop_time < self.BTN_BALLOON_POP_TIME:
                    self.a_balloon_pop_time += dt
                    x = min(self.a_balloon_pop_time / self.BTN_BALLOON_POP_TIME, 1)
                    scale = ((x if x < 0.5 else (1 - x)) * self.BTN_BALLOON_POP_SCALAR) + 1
                    balloon_size = (self.a_balloon_orig_size[0] * scale, self.a_balloon_orig_size[1] * scale)
                    self.a_balloon_invert = pygame.transform.scale(self.a_balloon_invert_orig.copy(), balloon_size)
                    self.a_balloon_invert_pos = self.a_balloon_invert.get_rect(centerx=self.a_balloon_anchor[0], bottom=self.a_balloon_anchor[1])

                if (not self.b_pressed and wm_state.b_btn) or (self.b_pressed and not wm_state.b_btn):
                    self.b_alpha_time = 0
                    self.b_pressed = wm_state.b_btn
                    self.b_balloon_pop_time = 0
                if self.b_alpha_time < self.BTN_FADE_TIME:
                    self.b_alpha_time += dt
                    x = min(self.b_alpha_time / self.BTN_FADE_TIME, 1)
                    alpha = (x if self.b_pressed else (1 - x)) * 255
                    self.b_alpha_surf.set_alpha(alpha)
                if self.b_pressed and self.b_balloon_pop_time < self.BTN_BALLOON_POP_TIME:
                    self.b_balloon_pop_time += dt
                    x = min(self.b_balloon_pop_time / self.BTN_BALLOON_POP_TIME, 1)
                    scale = ((x if x < 0.5 else (1 - x)) * self.BTN_BALLOON_POP_SCALAR) + 1
                    balloon_size = (self.b_balloon_orig_size[0] * scale, self.b_balloon_orig_size[1] * scale)
                    self.b_balloon_invert = pygame.transform.scale(self.b_balloon_invert_orig.copy(), balloon_size)
                    self.b_balloon_invert_pos = self.b_balloon_invert.get_rect(right=self.b_balloon_anchor[0], top=self.b_balloon_anchor[1])

                if self.a_pressed or self.b_pressed:
                    if self.press_btns_pop_time < self.PRESS_BTN_POP_TIME:
                        self.press_btns_pop_time += dt
                        x = min(self.press_btns_pop_time / self.PRESS_BTN_POP_TIME, 1)
                        scale = 1 - ((x if x < 0.5 else (1 - x)) * self.PRESS_BTN_POP_SCALE_TO)
                        press_btns_size = (self.press_btns_orig_size[0], self.press_btns_orig_size[1] * scale)
                        self.press_btns_img = pygame.transform.scale(self.press_btns_orig_img.copy(), press_btns_size)
                elif self.press_btns_pop_time > 0:
                    self.press_btns_pop_time = 0
                    self.press_btns_img = pygame.transform.scale(self.press_btns_orig_img.copy(), self.press_btns_orig_size)

                if self.a_pressed and self.b_pressed:
                    self.ready_time += dt
                    if self.ready_time >= self.READY_TIME:
                        self.state = UIObjTitleStates.FADING_OUT
                else:
                    self.ready_time = 0
            case UIObjTitleStates.FADING_OUT:
                self.fade_out_time += dt
                self.alpha = (1 - min(self.fade_out_time / self.FADE_OUT_TIME, 1)) * 255
                if self.fade_out_time >= self.FADE_OUT_TIME:
                    self.is_complete = True
                    return [(UIObjWelcomeIn, Constants.EVENT_HOME_READY)]
        return []

    def draw(self, display):
        if self.state == UIObjTitleStates.WAITING_FOR_FADE:
            return

        if self.alpha > 0:
            self.alpha_surf.fill((0, 0, 0, 0))
            self.alpha_surf.blit(self.title_img, (0,0))
            if self.a_alpha >= 0:
                self.alpha_surf.blit(self.a_alpha_surf, (0,0))
            if self.b_alpha >= 0:
                self.alpha_surf.blit(self.b_alpha_surf, (0,0))
            press_btns_pos = self.press_btns_img.get_rect(left=self.press_btns_anchor[0], bottom=self.press_btns_anchor[1] + self.press_btns_y_offset)
            self.alpha_surf.blit(self.press_btns_img, press_btns_pos)
            if self.a_pressed:
                self.alpha_surf.blit(self.a_balloon_invert, self.a_balloon_invert_pos)
            else:
                self.alpha_surf.blit(self.a_balloon, self.a_balloon_pos)
            if self.b_pressed:
                self.alpha_surf.blit(self.b_balloon_invert, self.b_balloon_invert_pos)
            else:
                self.alpha_surf.blit(self.b_balloon, self.b_balloon_pos)

            temp_surf = self.alpha_surf.copy()
            temp_surf.set_alpha(self.alpha)
            display.blit(temp_surf, self.title_pos)

######################################################

class UIObjBackground(UIObject):
    def __init__(self, display_size):
        super().__init__()

        self.video = cv2.VideoCapture('assets/video/wuhu-island.webm')
        self.can_show_video, video_image = self.video.read()
        video_size = video_image.shape[1::-1]
        video_x_scale = display_size[0] / video_size[0]
        video_y_scale = display_size[1] / video_size[1]
        video_scale = max(video_x_scale, video_y_scale)
        self.video_size = (int(video_size[0] * video_scale), int(video_size[1] * video_scale))
        self.video_pos = ((display_size[0] - self.video_size[0]) * 0.5, (display_size[1] - self.video_size[1]) * 0.5)

        background_img = pygame.image.load('assets/images/home/wuhu-island.jpg').convert_alpha()
        background_size = background_img.get_size()
        background_x_scale = display_size[0] / background_size[0]
        background_y_scale = display_size[1] / background_size[1]
        background_scale = max(background_x_scale, background_y_scale)
        background_size = (int(background_size[0] * background_scale), int(background_size[1] * background_scale))
        self.background_img = pygame.transform.scale(background_img, background_size)
        self.background_pos = self.background_img.get_rect(centerx=display_size[0] * 0.5, centery=display_size[1] * 0.5)

    def update(self, dt, incoming_events, wm_state):
        self.can_show_video, video_image = self.video.read()
        if self.can_show_video:
            video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], 'BGR')
            self.video_surf = pygame.transform.scale(video_surf, self.video_size)
        return []

    def draw(self, display):
        if self.can_show_video and self.video_surf:
            display.blit(self.video_surf, self.video_pos)
        else:
            display.blit(self.background_img, self.background_pos)



######################################################
#                      Screen                        #
######################################################


class HomeScreen(Screen):
    @property
    def screen_state(self):
        return ScreenStates.HOME_SCREEN

    @property
    def background_color(self):
        return '#000000'

    def __init__(self, display, init_events):
        super().__init__(display, init_events)
        self.active_objs = [
            UIObjBackground(self.display_size),
            UIObjTitle(self.display_size),
            UIObjIntroFade(self.display_size),
            UIObjDisconnectedFadeOut(self.display_size),
            UIObjWelcomeIn(self.display_size)
        ]