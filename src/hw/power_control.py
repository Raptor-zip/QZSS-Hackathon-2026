from gpiozero import OutputDevice
import logging

class RelayController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Relay GPIO configuration (Based on test/relay_keyboard.py)
        # Low active assumption or High active?
        # test/relay_keyboard.py used active_high=True
        try:
            self.relays = {
                1: OutputDevice(4, active_high=True, initial_value=False),
                2: OutputDevice(17, active_high=True, initial_value=False),
                3: OutputDevice(27, active_high=True, initial_value=False),
                4: OutputDevice(22, active_high=True, initial_value=False)
            }
        except Exception as e:
            self.logger.warning(f"GPIO Error: {e}. Using Mock Relays.")
            class MockRelay:
                def __init__(self): self.value = False
                def on(self): self.value = True
                def off(self): self.value = False
            self.relays = {i: MockRelay() for i in range(1, 5)}

    def set_relay(self, relay_id, state):
        """
        Set specific relay state.
        :param relay_id: 1-4
        :param state: True (ON), False (OFF)
        """
        if relay_id in self.relays:
            if state:
                self.relays[relay_id].on()
            else:
                self.relays[relay_id].off()
            self.logger.info(f"Relay {relay_id} set to {'ON' if state else 'OFF'}")

    def toggle(self, relay_id):
        """Toggle relay state"""
        if relay_id in self.relays:
            if self.relays[relay_id].value: # Currently ON (Value 1)
                 self.set_relay(relay_id, False)
            else:
                 self.set_relay(relay_id, True)

    def all_on(self):
        """Turn multiple relays ON (e.g. for Recovery)"""
        for r in self.relays.values():
            r.on()
        self.logger.info("All relays ON")

    def all_off(self):
        """Turn ALL relays OFF (Safety Cutoff)"""
        for r in self.relays.values():
            r.off()
        self.logger.info("All relays OFF (CUTOFF)")

    def get_status(self):
        return {k: v.value for k, v in self.relays.items()}
