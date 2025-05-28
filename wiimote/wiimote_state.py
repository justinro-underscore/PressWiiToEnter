class WiimoteState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.connected = False
        self.acc = (0, 0, 0)

    def as_dict(self):
        return {
            'connected': self.connected,
            'acc': self.acc
        }