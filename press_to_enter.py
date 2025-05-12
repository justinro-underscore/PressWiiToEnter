from ui.ui_runner import UIRunner
from wiimote.wiimote_runner import WiimoteRunner

ui_runner = UIRunner()
wm_runner = WiimoteRunner()

while ui_runner.is_running():
    wm_runner.update()
    wm_runner.try_connect()
    ui_runner.draw()

ui_runner.quit()