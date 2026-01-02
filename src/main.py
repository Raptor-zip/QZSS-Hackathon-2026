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
from src.client.socket_client import SocketIOClient
from src.gui.app_window import AppWindow

def main():
    # Setup Logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("Main")

    try:
        logger.info("Initializing Hardware...")
        qz1 = QZ1Handler()
        imu = IMUHandler()

        # Define callback wrapper for PowerControl
        # We need access to socket_client, which is defined later.
        # Use a mutable container or late binding.
        client_container = {}
        def power_callback(status):
            if 'client' in client_container:
                client_container['client'].emit_status(status)

        power = RelayController(callback=power_callback)
        audio = AudioHandler()

        logger.info("Initializing Core Logic...")
        sm = StateMachine(qz1, imu, power, audio)

        logger.info("Initializing Socket.IO Client...")
        socket_client = SocketIOClient(sm)
        client_container['client'] = socket_client
        socket_client.start()

        logger.info("Initializing Controls...")
        # Bind buttons to SM
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
        if 'socket_client' in locals(): socket_client.stop()
        if 'sm' in locals(): sm.stop()
        if 'buttons' in locals(): buttons.cleanup()

if __name__ == "__main__":
    main()
