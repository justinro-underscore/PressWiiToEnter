import pygame
from enum import Enum
from ui.screens.constants import Constants
from ui.screens.easings import ease_in_out_cubic, ease_in_out_quad, ease_out_sine, ease_out_elastic, ease_none
from ui.screens.screen import Screen, ScreenStates
from ui.screens.ui_object import UIObject


######################################################
#                    UI Objects                      #
######################################################


class UIObjFadeOut(UIObject):
    FADE_LENGTH = 1.5

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
            a = int(255 * ease_none(progress))
            self.surf.set_alpha(a)
            if progress >= 1:
                if wm_state.connected:
                    return ScreenStates.HOME_SCREEN
                else:
                    return (ScreenStates.INTRO_CONNECT_SCREEN, Constants.EVENT_FROM_WHITE_SCREEN)
        elif Constants.EVENT_CALIBRATION_DONE in incoming_events:
            self.fading = True
        return []

    def draw(self, display):
        display.blit(self.surf, (0,0))

######################################################

class WiimotePlayerStates(Enum):
    ENTERING = 1
    CALIBRATING = 2
    CALIBRATING_DONE = 3

# NOTE: Not really used as a UI Object, purely inherits UIObject to use the helper methods
class WiimotePlayerUI(UIObject):
    CALIBRATION_BAR_TOP_PERCENT = 0.623148148

    CALIBRATION_TEXT_ALPHA_TIME = 0.6

    WIIMOTE_ROTATION_SCALAR = 1
    WIIMOTE_ROTATION_PURE_CLOCKWISE = False
    WIIMOTE_ROTATION_LERP = 0.6

    CALIBRATION_ROT_THRESHOLD = 2
    CALIBRATION_TIME = 4

    CALIBRATION_DONE_MOVE_TIME = 0.6
    CALIBRATION_DONE_WAIT_TIME = 1

    def pop_ease(self, pop_time):
        if pop_time > self.POP_TIME:
            pop_time = self.POP_TIME

        grow_threshold = self.POP_TIME * self.POP_GROW_PERCENT
        if pop_time <= grow_threshold:
            return ease_out_sine(pop_time / grow_threshold) * self.POP_SCALE
        else:
            return ((1 - ease_out_sine((pop_time - grow_threshold) / (self.POP_TIME - grow_threshold))) * (self.POP_SCALE - 1)) + 1

    def __init__(self, base_scale):
        super().__init__()
        self.state = WiimotePlayerStates.ENTERING

        self.surf_size = (326 * base_scale, 252 * base_scale)
        self.surf = pygame.Surface(self.surf_size, pygame.SRCALPHA)

        player_one_img = pygame.image.load('assets/images/wiimote-player-1.png').convert_alpha()
        self.player_one_size = player_one_img.get_size()
        self.player_one_size = (self.player_one_size[0] * base_scale, self.player_one_size[1] * base_scale)
        self.player_one_img = pygame.transform.scale(player_one_img, self.player_one_size)
        self.player_one_pos = self.player_one_img.get_rect(centerx=self.surf_size[0] * 0.5, centery=5 + (self.player_one_size[1] * 0.5))

        calibrating_dark_img = pygame.image.load('assets/images/calibrating-dark.png').convert_alpha()
        calibrating_bright_img = pygame.image.load('assets/images/calibrating-bright.png').convert_alpha()
        calibrating_ok_img = pygame.image.load('assets/images/calibrating-ok.png').convert_alpha()

        calibrating_text_size = calibrating_dark_img.get_size() # All calibrating images should have the same size and the same position
        calibrating_text_size = (calibrating_text_size[0] * base_scale, calibrating_text_size[1] * base_scale)
        self.calibrating_text_pos = (10 * base_scale, 60 * base_scale)

        self.calibrating_dark_img = pygame.transform.scale(calibrating_dark_img, calibrating_text_size)

        self.calibrating_alpha_surf = pygame.Surface(calibrating_text_size, pygame.SRCALPHA).convert()
        self.calibrating_alpha_surf_alpha = 0
        self.calibrating_bright_img = pygame.transform.scale(calibrating_bright_img, calibrating_text_size)
        self.calibrating_alpha_time = 0

        self.calibrating_ok_img = pygame.transform.scale(calibrating_ok_img, calibrating_text_size)

        wiimote_img = pygame.image.load('assets/images/wiimote.png').convert_alpha()
        self.wiimote_size = wiimote_img.get_size()
        self.wiimote_size = (self.wiimote_size[0] * base_scale, self.wiimote_size[1] * base_scale)
        self.wiimote_orig_img = pygame.transform.scale(wiimote_img, self.wiimote_size)
        self.rotate_wiimote(0)
        self.wiimote_rot = 0
        self.wiimote_rot_target = 0

        self.calibration_time = 0
        self.last_wm_acc = None
        self.wiimote_done_time = 0

    def calibration_bar_done_entering(self):
        self.state = WiimotePlayerStates.CALIBRATING

    def update(self, dt, calibration_bar_events, wm_state):
        match self.state:
            case WiimotePlayerStates.ENTERING:
                pass
            case WiimotePlayerStates.CALIBRATING:
                self.calibrating_alpha_time += dt
                alpha_time_phase_idx = self.calibrating_alpha_time // self.CALIBRATION_TEXT_ALPHA_TIME
                brightening = alpha_time_phase_idx % 2 == 0
                x = self.calibrating_alpha_time % self.CALIBRATION_TEXT_ALPHA_TIME
                self.calibrating_alpha_surf_alpha = int(ease_in_out_quad(x if brightening else (1 - x)) * 255)

                abs_change_delta = 0
                if self.last_wm_acc is not None:
                    change_delta = 0
                    for i in range(len(wm_state.acc)):
                        delta = wm_state.acc[i] - self.last_wm_acc[i]
                        change_delta += delta
                        abs_change_delta += abs(delta)
                    rot_delta = -abs(change_delta) if self.WIIMOTE_ROTATION_PURE_CLOCKWISE else change_delta
                    self.wiimote_rot_target += rot_delta * self.WIIMOTE_ROTATION_SCALAR
                    self.wiimote_rot = ((self.wiimote_rot_target - self.wiimote_rot) * (self.WIIMOTE_ROTATION_LERP * dt)) + self.wiimote_rot
                self.last_wm_acc = wm_state.acc

                if self.wiimote_rot != self.wiimote_rot_target:
                    self.wiimote_img = pygame.transform.rotate(self.wiimote_orig_img.copy(), self.wiimote_rot)
                    self.wiimote_pos = self.wiimote_img.get_rect(centerx=self.surf_size[0] * 0.5, centery=45 + (self.surf_size[1] * 0.5))

                if abs_change_delta < self.CALIBRATION_ROT_THRESHOLD:
                    self.calibration_time += dt
                    if self.calibration_time >= self.CALIBRATION_TIME:
                        self.wiimote_rot = self.wiimote_rot % 360
                        if self.wiimote_rot < 0: self.wiimote_rot += 360
                        if self.wiimote_rot > 180: self.wiimote_rot -= 360
                        self.wiimote_rot_target = 0
                        self.state = WiimotePlayerStates.CALIBRATING_DONE
                        return [(UIObjInfoDialog, Constants.EVENT_CALIBRATION_DONE)]
                else:
                    self.calibration_time = 0

            case WiimotePlayerStates.CALIBRATING_DONE:
                self.wiimote_done_time += dt
                rot_x = self.wiimote_done_time / self.CALIBRATION_DONE_MOVE_TIME
                if rot_x <= 1:
                    wiimote_rot = ((self.wiimote_rot_target - self.wiimote_rot) * ease_out_elastic(rot_x)) + self.wiimote_rot
                    self.rotate_wiimote(wiimote_rot)
                elif self.wiimote_done_time / (self.CALIBRATION_DONE_MOVE_TIME + self.CALIBRATION_DONE_WAIT_TIME) >= 1:
                    self.is_complete = True
                    return [(UIObjFadeOut, Constants.EVENT_CALIBRATION_DONE)]

        return []

    def rotate_wiimote(self, rot):
        self.wiimote_img = pygame.transform.rotate(self.wiimote_orig_img.copy(), rot)
        self.wiimote_pos = self.wiimote_img.get_rect(centerx=self.surf_size[0] * 0.5, centery=45 + (self.surf_size[1] * 0.5))

    def create_draw(self):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.player_one_img, self.player_one_pos)
        if self.state != WiimotePlayerStates.CALIBRATING_DONE:
            self.surf.blit(self.calibrating_dark_img, self.calibrating_text_pos)

            if self.calibrating_alpha_surf_alpha >= 0:
                self.calibrating_alpha_surf.fill((0, 0, 0, 0))
                self.calibrating_alpha_surf.blit(self.calibrating_bright_img, (0, 0))
                temp_surf = self.calibrating_alpha_surf.copy()
                temp_surf.set_alpha(self.calibrating_alpha_surf_alpha)
                self.surf.blit(temp_surf, self.calibrating_text_pos)
        else:
            self.surf.blit(self.calibrating_ok_img, self.calibrating_text_pos)
        self.surf.blit(self.wiimote_img, self.wiimote_pos)
        return self.surf

######################################################

class CalibrationBarStates(Enum):
    ENTERING = 1
    IDLE = 2
    EXITING = 3

class UIObjCalibrationBar(UIObject):
    CALIBRATION_BAR_TOP_PERCENT = 0.623148148

    def __init__(self, display_size, calibration_bar_img):
        super().__init__()
        self.state = CalibrationBarStates.ENTERING

        self.calibration_bar_top_pos = display_size[1] * self.CALIBRATION_BAR_TOP_PERCENT
        calibration_bar_size = calibration_bar_img.get_size()
        calibration_bar_height = display_size[1] - self.calibration_bar_top_pos
        scale = calibration_bar_height / calibration_bar_size[1]
        calibration_bar_size = (calibration_bar_size[0] * scale, calibration_bar_size[1] * scale)
        self.calibration_bar_img = pygame.transform.scale(calibration_bar_img, calibration_bar_size)
        self.calibration_bar_start = display_size[1]
        self.move_distance = abs(self.calibration_bar_start - self.calibration_bar_top_pos)
        self.calibration_bar_pos = self.calibration_bar_img.get_rect(centerx=display_size[0] * 0.5, top=self.calibration_bar_start)

        self.move_time = 0

        self.wiimote_pos = (784 * scale, 4 * scale)
        self.wiimote = WiimotePlayerUI(scale)

    def update(self, dt, incoming_events, wm_state):
        if Constants.EVENT_CALIBRATION_EXITING in incoming_events:
            self.state = CalibrationBarStates.EXITING

        if self.state != CalibrationBarStates.EXITING and not self.wiimote.is_complete:
            wiimote_events = self.wiimote.update(dt, incoming_events, wm_state)
            if len(wiimote_events) > 0:
                return wiimote_events

        match self.state:
            case CalibrationBarStates.ENTERING:
                self.move_time += dt
                new_y = self.calibration_bar_start - (ease_in_out_cubic(self.move_time / Constants.CALIBRATION_ENTER_TIME) * self.move_distance)
                self.calibration_bar_pos[1] = max(new_y, self.calibration_bar_top_pos)
                if self.calibration_bar_pos[1] <= self.calibration_bar_top_pos:
                    self.move_time = 0
                    self.wiimote.calibration_bar_done_entering()
                    self.state = CalibrationBarStates.IDLE
            case CalibrationBarStates.IDLE:
                pass
            case CalibrationBarStates.EXITING:
                self.move_time += dt
                new_y = self.calibration_bar_top_pos + (ease_in_out_cubic(self.move_time / Constants.CALIBRATION_EXIT_TIME) * self.move_distance)
                self.calibration_bar_pos[1] = min(new_y, self.calibration_bar_start)
                if self.calibration_bar_pos[1] >= self.calibration_bar_start:
                    self.is_complete = True
        return []

    def draw(self, display):
        display.blit(self.calibration_bar_img, self.calibration_bar_pos)
        display.blit(self.wiimote.create_draw(), (self.calibration_bar_pos[0] + self.wiimote_pos[0], self.calibration_bar_pos[1] + self.wiimote_pos[1]))

######################################################

class InfoDialogStates(Enum):
    SHRINKING = 1
    FADING_IN = 2
    IDLE = 3
    FADING_OUT = 4
    GROWING = 5

class UIObjInfoDialog(UIObject):
    FADE_IN_TIME = 1
    FADE_OUT_TIME = 0.3

    DIALOG_END_OFFSET_PERCENT = 0.037962963
    DIALOG_END_BOTTOM_PERCENT = 0.61944444

    def __init__(self, display_size, dialog_img, lay_flat_img):
        super().__init__()
        self.state = InfoDialogStates.SHRINKING

        self.orig_dialog_img = dialog_img
        dialog_size = dialog_img.get_size()
        x_scale = (display_size[0] - (Constants.DIALOG_OFFSET * 2)) / dialog_size[0]
        y_scale = (display_size[1] - (Constants.DIALOG_OFFSET * 2)) / dialog_size[1]
        scale = min(x_scale, y_scale)
        self.start_dialog_size = (int(dialog_size[0] * scale), int(dialog_size[1] * scale))
        self.start_dialog_pos = ((display_size[0] - self.start_dialog_size[0]) / 2, (display_size[1] - self.start_dialog_size[1]) / 2)

        end_dialog_height = display_size[1] * (self.DIALOG_END_BOTTOM_PERCENT - self.DIALOG_END_OFFSET_PERCENT)
        end_scale = end_dialog_height / dialog_size[1]
        self.end_dialog_size = (int(dialog_size[0] * end_scale), int(dialog_size[1] * end_scale))
        self.end_dialog_pos = ((display_size[0] - self.end_dialog_size[0]) / 2, display_size[1] * self.DIALOG_END_OFFSET_PERCENT)

        self.dialog_img = pygame.transform.scale(dialog_img, self.start_dialog_size)
        self.dialog_pos = self.start_dialog_pos

        self.scale_time = 0

        self.alpha = 0
        self.alpha_time = 0
        self.alpha_surf = pygame.Surface(self.end_dialog_size, pygame.SRCALPHA)
        self.alpha_surf.convert()

        lay_flat_size = lay_flat_img.get_size()
        lay_flat_size = (int(lay_flat_size[0] * end_scale * 0.5), int(lay_flat_size[1] * end_scale * 0.5))
        lay_flat_img_offset = (334, 37)
        self.lay_flat_pos = (lay_flat_img_offset[0] * end_scale, lay_flat_img_offset[1] * end_scale)
        self.lay_flat_img_orig = pygame.transform.scale(lay_flat_img, lay_flat_size)

        font_size = int(72 * end_scale)
        font = pygame.font.Font('assets/fonts/contb.ttf', font_size)
        self.text1 = font.render('Place the Wii Remote on a', True, '#888888')
        self.text1_pos = self.text1.get_rect(centerx=self.end_dialog_size[0] * 0.5, centery=self.end_dialog_size[1] * 0.69)
        self.text2 = font.render('flat surface and keep it still.', True, '#888888')
        self.text2_pos = self.text2.get_rect(centerx=self.end_dialog_size[0] * 0.5, top=self.text1_pos[1] + font_size)

        self.calibrated = False

    def update(self, dt, incoming_events, wm_state):
        if self.calibrated:
            return []

        match self.state:
            case InfoDialogStates.SHRINKING:
                self.scale_time += dt
                x = ease_in_out_cubic(self.scale_time / Constants.CALIBRATION_ENTER_TIME)
                dialog_size = ((self.end_dialog_size[0] - self.start_dialog_size[0]) * x + self.start_dialog_size[0],
                               (self.end_dialog_size[1] - self.start_dialog_size[1]) * x + self.start_dialog_size[1])
                self.dialog_img = self.orig_dialog_img.copy()
                self.dialog_img = pygame.transform.scale(self.dialog_img, dialog_size)
                self.dialog_pos = ((self.end_dialog_pos[0] - self.start_dialog_pos[0]) * x + self.start_dialog_pos[0],
                                   (self.end_dialog_pos[1] - self.start_dialog_pos[1]) * x + self.start_dialog_pos[1])
                if x >= 1:
                    self.scale_time = 0
                    if wm_state.connected:
                        self.state = InfoDialogStates.FADING_IN
                    else:
                        self.state = InfoDialogStates.GROWING
                        return [(UIObjCalibrationBar, Constants.EVENT_CALIBRATION_EXITING)]
            case InfoDialogStates.FADING_IN:
                self.alpha_time += dt
                self.alpha = min((self.alpha_time / self.FADE_IN_TIME) * 255, 255)
                if self.alpha == 255:
                    self.alpha_time = 0
                    self.state = InfoDialogStates.IDLE
            case InfoDialogStates.IDLE:
                if Constants.EVENT_CALIBRATION_DONE in incoming_events:
                    self.calibrated = True
                    return []

                if not wm_state.connected:
                    self.state = InfoDialogStates.FADING_OUT
            case InfoDialogStates.FADING_OUT:
                self.alpha_time += dt
                self.alpha = max(((self.FADE_OUT_TIME - self.alpha_time) / self.FADE_OUT_TIME) * 255, 0)
                if self.alpha == 0:
                    self.state = InfoDialogStates.GROWING
                    return [(UIObjCalibrationBar, Constants.EVENT_CALIBRATION_EXITING)]
            case InfoDialogStates.GROWING:
                self.scale_time += dt
                x = ease_in_out_cubic(self.scale_time / Constants.CALIBRATION_EXIT_TIME)
                dialog_size = ((self.start_dialog_size[0] - self.end_dialog_size[0]) * x + self.end_dialog_size[0],
                               (self.start_dialog_size[1] - self.end_dialog_size[1]) * x + self.end_dialog_size[1])
                self.dialog_img = self.orig_dialog_img.copy()
                self.dialog_img = pygame.transform.scale(self.dialog_img, dialog_size)
                self.dialog_pos = ((self.start_dialog_pos[0] - self.end_dialog_pos[0]) * x + self.end_dialog_pos[0],
                                   (self.start_dialog_pos[1] - self.end_dialog_pos[1]) * x + self.end_dialog_pos[1])
                if x >= 1:
                    return (ScreenStates.INTRO_CONNECT_SCREEN, Constants.EVENT_FROM_DIALOG)
        return []

    def draw(self, display):
        display.blit(self.dialog_img, self.dialog_pos)

        if self.alpha >= 0:
            self.alpha_surf.fill((0, 0, 0, 0))
            self.alpha_surf.blit(self.lay_flat_img_orig, self.lay_flat_pos)
            self.alpha_surf.blit(self.text1, self.text1_pos)
            self.alpha_surf.blit(self.text2, self.text2_pos)
            temp_surf = self.alpha_surf.copy()
            temp_surf.set_alpha(self.alpha)
            display.blit(temp_surf, self.dialog_pos)



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

    def __init__(self, display, init_events):
        super().__init__(display, init_events)
        display_size = display.get_size()
        dialog_img = pygame.image.load(Constants.DIALOG_IMG_FILE).convert_alpha()
        lay_flat_img = pygame.image.load('assets/images/lay-flat_upscaled.png').convert_alpha()
        calibration_bar_img = pygame.image.load('assets/images/calibration-bar.png').convert_alpha()
        self.active_objs = [
            UIObjInfoDialog(display_size, dialog_img, lay_flat_img),
            UIObjCalibrationBar(display_size, calibration_bar_img),
            UIObjFadeOut(display_size)
        ]