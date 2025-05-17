class UIObject:
    def __init__(self):
        self.is_complete = False
        pass

    # Returns a list of outgoing events
    def update(self, dt, incoming_events):
        return []

    def draw(self, display):
        pass