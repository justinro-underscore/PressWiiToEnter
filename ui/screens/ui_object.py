from ui.screens.constants import Constants

class UIObject:
    def __init__(self):
        self.is_complete = False
        pass

    # Returns a list of outgoing events
    def update(self, dt, incoming_ui_events, wm_state):
        return []

    def draw(self, display):
        pass

    def get_keydown_in_events(self, events, expected_key):
        for event in events:
            if event.find(Constants.EVENT_KEYDOWN) == 0:
                key = int(event[len(Constants.EVENT_KEYDOWN):])
                if key == expected_key:
                    return True
        return False