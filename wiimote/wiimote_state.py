class WiimoteState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.connected = False
        self.acc = (0, 0, 0)
        self.a_btn = False
        self.b_btn = False

    def as_dict(self):
        return {
            'connected': self.connected,
            'acc': self.acc,
            'a_btn': self.a_btn,
            'b_btn': self.b_btn
        }