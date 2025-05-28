import cwiid
import time

def wiimote_handler(q):
    def try_connect():
        try:
            wiimote = cwiid.Wiimote()
            if wiimote:
                wiimote.led = 1
                wiimote.rpt_mode = cwiid.RPT_ACC
                return wiimote
        except RuntimeError:
            pass

    def try_get_state(wiimote):
        try:
            wiimote.request_status() # Will hang if we lose connection
            return wiimote.state
        except RuntimeError as e:
            return {'wiimote_error': e}

    wm = None
    try:
        while True:
            if not wm:
                wm = try_connect()
                if wm:
                    q.put(True)
            else:
                wm_state = try_get_state(wm)
                q.put(wm_state)

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        q.put({'wiimote_error': str(e)})
        pass

    if wm:
        wm.close()
    q.put({'wiimote_error': -1})
