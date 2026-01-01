from gpiozero import Button
import logging

class ButtonHandler:
    def __init__(self, callbacks=None):
        """
        :param callbacks: Dictionary mapping button ID (1-5) to callback functions
        """
        self.logger = logging.getLogger(__name__)
        # Assigning GPIO pins for 5 buttons.
        # Avoid 2, 3 (I2C), 4, 17, 27, 22 (Relays), 14, 15 (UART for QZ1/Console)
        # Using: 5, 6, 13, 19, 26
        self.pin_map = {
            1: 5,
            2: 6,
            3: 13,
            4: 19,
            5: 26
        }
        self.buttons = {}

        for btn_id, pin in self.pin_map.items():
            try:
                # pull_up=True is default for Button class? Documentation says yes generally for simple connection to GND.
                # User specified "Pull up input".
                self.buttons[btn_id] = Button(pin, pull_up=True, bounce_time=0.1)

                # Setup callbacks if provided
                if callbacks and btn_id in callbacks:
                    self.buttons[btn_id].when_pressed = callbacks[btn_id]

            except Exception as e:
                self.logger.warning(f"Failed to init Button {btn_id} on Pin {pin}: {e}. Using Mock.")
                class MockBtn:
                    def __init__(self): self.when_pressed = None
                    def close(self): pass
                self.buttons[btn_id] = MockBtn()
                if callbacks and btn_id in callbacks:
                    self.buttons[btn_id].when_pressed = callbacks[btn_id]

    def assign_callback(self, btn_id, callback):
        if btn_id in self.buttons:
            self.buttons[btn_id].when_pressed = callback

    def cleanup(self):
        for btn in self.buttons.values():
            btn.close()
