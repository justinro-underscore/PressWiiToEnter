import cwiid
import threading
from wiimote.wiimote_state import WiimoteState

class WiimoteRunner:
    def __init__(self):
        self.running = True
        self.wm = None
        self.wm_state = WiimoteState()

        self.connecting_thread = None
        self.connecting = False

    def update(self):
        if not self.wm_state.connected and not self.connecting:
            self.try_connect()

    def try_connect(self):
        if self.wm or self.connecting:
            return

        self.connecting = True
        self.connecting_thread = threading.Thread(target=self.infinite_connect)
        self.connecting_thread.start()

    def infinite_connect(self):
        while not self.wm and self.running:
            try:
                self.wm = cwiid.Wiimote()
            except RuntimeError:
                print("Trying again...")
        if not self.running:
            return
        self.wm.led = 1
        self.connecting = False
        self.wm_state.connected = True
    
    def on_exit(self):
        self.running = False
        self.connecting_thread.join()