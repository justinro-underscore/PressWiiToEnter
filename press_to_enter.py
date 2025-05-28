import sys
from ui.ui_runner import UIRunner
from wiimote.wiimote_runner import WiimoteRunner

ui_runner = UIRunner()
wm_runner = WiimoteRunner()

breaking_exception = None
try:
    while ui_runner.is_running():
        ui_runner.update(wm_runner.wm_state)
except KeyboardInterrupt:
    pass
except Exception as e:
    breaking_exception = e

ui_runner.quit()
wm_runner.on_exit()

if breaking_exception is not None:
    raise breaking_exception
else:
    sys.exit()