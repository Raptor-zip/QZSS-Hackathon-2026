from gpiozero import PWMOutputDevice
import time
import threading
import logging

class AudioHandler:
    def __init__(self, pin=12):
        self.logger = logging.getLogger(__name__)
        # Using GPIO 12 (PWM0) for audio output (buzzer or speaker driver)
        try:
            self.device = PWMOutputDevice(pin, frequency=440)
        except Exception as e:
            self.logger.warning(f"Audio GPIO Init Failed: {e}. Using Mock Audio.")
            class MockAudio:
                def __init__(self): self.frequency = 440; self.value = 0
            self.device = MockAudio()
        self.running = False
        self.thread = None

    def play_tone(self, frequency=440, duration=0.5):
        self.device.frequency = frequency
        self.device.value = 0.5 # 50% duty cycle
        time.sleep(duration)
        self.device.value = 0

    def start_alarm(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._alarm_loop, daemon=True)
        self.thread.start()
        self.logger.info("Alarm started")

    def stop_alarm(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.device.value = 0
        self.logger.info("Alarm stopped")

    def _alarm_loop(self):
        while self.running:
            # Emergency Siren Pattern
            self.play_tone(880, 0.5)
            if not self.running: break
            self.play_tone(440, 0.5)
            if not self.running: break
