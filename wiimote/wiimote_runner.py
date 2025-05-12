import cwiid
import threading

class WiimoteRunner:
    def __init__(self):
        self.wm = None
        self.connecting_thread = None
        self.connecting = False
        pass

    def update(self):
        pass

    def try_connect(self):
        if self.wm or self.connecting:
            return

        self.connecting = True
        self.connecting_thread = threading.Thread(target=self.infinite_connect)

    def infinite_connect(self):
        while not self.wm:
            try:
                self.wm = cwiid.Wiimote()
            except RuntimeError:
                print("Trying again...")
        self.connecting = False