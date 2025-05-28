from enum import Enum

class ScreenStates(Enum):
    INTRO_CONNECT_SCREEN = 1
    INTRO_PICKUP_SCREEN = 2
    CALIBRATION_SCREEN = 3
    HOME_SCREEN = 4
    WELCOME_SCREEN = 5

class Screen:
    @property
    def screen_state(self):
        return None

    @property
    def background_color(self):
        return 'black'

    def __init__(self, display, init_events):
        self.display = display
        self.active_objs = []
        self.events = {}

    def update(self, dt, wm_state):
        upcoming_events = {}
        for obj in self.active_objs:
            events = []
            if type(obj) in self.events:
                events = self.events[type(obj)]
            new_events = obj.update(dt, events, wm_state)
            if new_events is not None:
                if isinstance(new_events, ScreenStates) or (len(new_events) > 0 and isinstance(new_events[0], ScreenStates)):
                    return new_events
                else:
                    for new_event in new_events:
                        event_class = new_event[0]
                        if event_class in upcoming_events:
                            upcoming_events[event_class] += new_event[1]
                        else:
                            upcoming_events[event_class] = new_event[1]
        self.events = upcoming_events

    def draw(self):
        for obj in self.active_objs:
            obj.draw(self.display)

    def clean(self):
        for i in range(len(self.active_objs) - 1, -1, -1):
            obj = self.active_objs[i]
            if obj.is_complete:
                self.active_objs.pop(i)