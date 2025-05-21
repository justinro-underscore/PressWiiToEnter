import sys
from ui.ui_runner import UIRunner
from wiimote.wiimote_runner import WiimoteRunner

ui_runner = UIRunner()
wm_runner = WiimoteRunner()

while ui_runner.is_running():
    wm_runner.update()
    ui_runner.update(wm_runner.wm_state)

ui_runner.quit()
wm_runner.on_exit()
sys.exit()