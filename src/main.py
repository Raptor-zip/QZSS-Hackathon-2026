import sys
import os
import logging

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.hw.qz1_handler import QZ1Handler
from src.hw.imu_handler import IMUHandler
from src.hw.power_control import RelayController
from src.hw.button_handler import ButtonHandler
from src.hw.audio import AudioHandler
from src.core.state_machine import StateMachine
from src.core.command_server import CommandServer
from src.gui.app_window import AppWindow

def main():
    # Setup Logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("Main")

    try:
        logger.info("Initializing Hardware...")
        qz1 = QZ1Handler()
        imu = IMUHandler()
        power = RelayController()
        audio = AudioHandler()

        logger.info("Initializing Core Logic...")
        sm = StateMachine(qz1, imu, power, audio)

        logger.info("Initializing Command Server...")
        cmd_server = CommandServer(sm)
        cmd_server.start()

        logger.info("Initializing Controls...")
        # Bind buttons to SM
        def btn_callback_wrapper(btn_object):
             # Extract ID from button object or map pins?
             # ButtonHandler logic: we passed callbacks. But we need SM initialized first.
             # Or we can assign specific callbacks now.
             pass

        # Since ButtonHandler expects callbacks or direct assignment:
        buttons = ButtonHandler()
        # Map buttons to SM actions
        buttons.assign_callback(1, lambda: sm.on_button_press(1))
        buttons.assign_callback(2, lambda: sm.on_button_press(2))
        buttons.assign_callback(3, lambda: sm.on_button_press(3))
        buttons.assign_callback(4, lambda: sm.on_button_press(4))
        buttons.assign_callback(5, lambda: sm.on_button_press(5))

        logger.info("Starting System...")
        sm.start()

        logger.info("Starting GUI...")
        app = AppWindow(sm)
        app.run() # Blocking call

    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.critical(f"Fatal Error: {e}", exc_info=True)
    finally:
        logger.info("Cleaning up...")
        if 'cmd_server' in locals(): cmd_server.stop()
        if 'sm' in locals(): sm.stop()
        if 'buttons' in locals(): buttons.cleanup()

if __name__ == "__main__":
    main()
