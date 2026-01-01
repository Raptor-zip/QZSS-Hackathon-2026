import logging
import time

class StateMachine:
    STATE_BOOT = "BOOT"
    STATE_NORMAL = "NORMAL"
    STATE_ALERT = "ALERT"
    STATE_RECOVERY = "RECOVERY"

    def __init__(self, qz1, imu, power, audio):
        self.qz1 = qz1
        self.imu = imu
        self.power = power
        self.audio = audio
        self.logger = logging.getLogger(__name__)

        self.current_state = self.STATE_BOOT
        self.alert_message = ""
        self.running = True

    def start(self):
        self.logger.info("Core Logic Started")
        self._transition_to(self.STATE_NORMAL)

        # Setup Callbacks
        self.qz1.callback = self.on_qz1_message
        self.imu.start_monitoring(self.on_imu_shake)
        self.qz1.start()

    def stop(self):
        self.running = False
        self.qz1.stop()
        self.imu.stop_monitoring()
        self.audio.stop_alarm()
        self.power.all_off() # Monitor specific behavior? keep running or cut?

    def _transition_to(self, new_state):
        self.logger.info(f"Transition: {self.current_state} -> {new_state}")
        self.current_state = new_state

        if new_state == self.STATE_NORMAL:
            self.power.all_on() # Restore power
            self.audio.stop_alarm()
            self.alert_message = ""

        elif new_state == self.STATE_ALERT:
            self.power.all_off() # SAFETY CUTOFF
            self.audio.start_alarm()

        elif new_state == self.STATE_RECOVERY:
            # Maybe waiting for confirmation
            self._transition_to(self.STATE_NORMAL)

    def on_qz1_message(self, report):
        self.logger.info(f"QZ1 Report: {report}")
        # Logic to determine if report is urgent
        # For now, treat any report as alert trigger
        self.alert_message = f"QZSS受信: {report}"
        if self.current_state != self.STATE_ALERT:
            self._transition_to(self.STATE_ALERT)

    def on_imu_shake(self, g_force):
        self.logger.info(f"IMU Shake: {g_force:.2f}G")
        if self.current_state != self.STATE_ALERT:
             self.alert_message = f"強い揺れを検知! ({g_force:.1f}G)"
             self._transition_to(self.STATE_ALERT)

    def on_button_press(self, btn_id):
        self.logger.info(f"Button {btn_id} pressed")
        # Button 1: Reset / Recovery (Any state)
        if btn_id == 1:
            if self.current_state == self.STATE_ALERT:
                self.logger.info("Manual Reset Triggered")
                self._transition_to(self.STATE_RECOVERY)
            elif self.current_state == self.STATE_RECOVERY:
                self._transition_to(self.STATE_NORMAL)

        # Power Control Buttons (Only in Normal Phase)
        if self.current_state == self.STATE_NORMAL:
            if btn_id == 2: # Relay 1
                self.power.toggle(1)
            if btn_id == 3: # Relay 2
                self.power.toggle(2)
            if btn_id == 4: # Relay 3
                self.power.toggle(3)

        # Test Trigger
        if self.current_state == self.STATE_NORMAL:
            if btn_id == 5: # Test Alert
                self.alert_message = "テスト警報 (ボタン5)"
                self._transition_to(self.STATE_ALERT)
