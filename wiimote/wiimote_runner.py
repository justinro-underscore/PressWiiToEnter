import threading
import time
from multiprocessing import Process, Queue, set_start_method
import os, signal
from wiimote.wiimote_state import WiimoteState
from wiimote.wiimote_handler import wiimote_handler

class WiimoteRunner:
    def __init__(self):
        self.running = True
        self.wm_state = WiimoteState()

        set_start_method('fork') # Note! This will only work on Mac/Linux!

        self.polling_thread = threading.Thread(target=self.start_polling)
        self.polling_thread.start()

    def kick_off_handler(self):
        self.wm_queue = Queue()
        self.wm_process = Process(target=wiimote_handler, args=(self.wm_queue,))
        self.wm_process.start()

    def terminate_handler(self):
        self.wm_state.reset()
        os.kill(self.wm_process.pid, signal.SIGINT)
        self.wm_process.terminate()
        self.wm_process.join()

    def start_polling(self):
        self.kick_off_handler()

        while self.running:
            time.sleep(0.1)

            try:
                # If we're not connected, keep polling the queue until we get a connection
                if not self.wm_state.connected:
                    try:
                        connected = self.wm_queue.get_nowait()
                        if connected == True:
                            print('Connected to Wiimote!')
                            self.wm_state.connected = True
                        else:
                            continue
                    except Exception:
                        continue

                # Once we have a connection, try to get the state with a timeout
                state = self.wm_queue.get(timeout=1.0)
                if 'wiimote_error' in state:
                    raise state['wiimote_error']
                else:
                    self.wm_state.acc = state['acc']
            except Exception:
                print('No response from Wiimote, killing process and trying again...')
                self.terminate_handler()
                self.kick_off_handler()

    def on_exit(self):
        self.running = False
        self.polling_thread.join()
        os.kill(self.wm_process.pid, signal.SIGINT)