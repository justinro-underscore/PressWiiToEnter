class UIObject:
    def __init__(self):
        self.is_complete = False
        pass

    # Returns a list of outgoing events
    def update(self, dt, incoming_ui_events, wm_state):
        return []

    def draw(self, display):
        pass