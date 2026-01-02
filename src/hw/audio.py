from gpiozero import PWMOutputDevice
import time
import threading
import logging
import os

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class AudioHandler:
    def __init__(self, pin=12, alert_file=None):
        self.logger = logging.getLogger(__name__)

        # Calculate default path relative to this file
        # src/hw/audio.py -> ../../assets/alert.wav
        if alert_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            alert_file = os.path.join(base_dir, "assets", "alert.wav")

        self.alert_file = alert_file
        self.using_pygame = False

        # 1. Try Pygame (Voice/High Quality Audio)
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.using_pygame = True
                self.logger.info("Audio: Pygame Mixer Initialized")
            except Exception as e:
                self.logger.warning(f"Audio: Pygame Init Failed: {e}")

        # 2. GPIO Buzzer Fallback
        self.buzzer = None
        try:
            self.buzzer = PWMOutputDevice(pin, frequency=440)
        except Exception as e:
            self.logger.warning(f"Audio: Buzzer GPIO Init Failed: {e}. Using Mock Buzzer.")
            class MockBuzzer:
                def __init__(self): self.frequency = 440; self.value = 0
            self.buzzer = MockBuzzer()

        self.running = False
        self.thread = None

    def play_tone(self, frequency=440, duration=0.5):
        if self.buzzer:
            self.buzzer.frequency = frequency
            self.buzzer.value = 0.5
            time.sleep(duration)
            self.buzzer.value = 0

    def start_alarm(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._alarm_loop, daemon=True)
        self.thread.start()
        self.logger.info("Alarm started")

    def stop_alarm(self):
        self.running = False
        if self.using_pygame and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        if self.thread:
            self.thread.join()

        if self.buzzer:
            self.buzzer.value = 0

        self.logger.info("Alarm stopped")

    def _alarm_loop(self):
        # Strategy:
        # If Pygame works and file exists -> Play Loop
        # Else -> Beep with Buzzer

        file_ready = False
        if self.using_pygame and os.path.exists(self.alert_file):
            try:
                pygame.mixer.music.load(self.alert_file)
                pygame.mixer.music.play(-1) # Loop forever
                file_ready = True
                self.logger.info(f"Audio: Playing {self.alert_file}")
            except Exception as e:
                self.logger.error(f"Audio: Failed to play file: {e}")

        # If file is playing, just wait (monitor stop signal)
        if file_ready:
            while self.running:
                time.sleep(0.5)
            # Stop handled in stop_alarm
            return

        # Fallback: Buzzer Siren
        self.logger.info("Audio: Fallback to Buzzer Siren")
        while self.running:
            self.play_tone(880, 0.5)
            if not self.running: break
            self.play_tone(440, 0.5)
            if not self.running: break
