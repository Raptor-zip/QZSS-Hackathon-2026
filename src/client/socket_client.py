import socketio
import logging
import threading
import time

class SocketIOClient:
    def __init__(self, state_machine, server_url='http://localhost:3000'):
        self.sm = state_machine
        self.server_url = server_url
        self.logger = logging.getLogger(__name__)
        self.sio = socketio.Client()
        self.running = False
        self.thread = None

        # Setup Events
        @self.sio.event
        def connect():
            self.logger.info("Connected to Web Server via Socket.IO")
            # Send initial status
            self.emit_status(self.sm.power.get_status())

        @self.sio.event
        def disconnect():
            self.logger.warning("Disconnected from Web Server")

        @self.sio.on('c2s_control')
        def on_control(data):
            self.logger.info(f"Received Control: {data}")
            try:
                if not isinstance(data, dict):
                    self.logger.error(f"Invalid data format: {type(data)}")
                    return

                cmd = data.get('cmd')

                # Handle 'get' command (No relay ID needed)
                if cmd == 'get':
                    self.emit_status(self.sm.power.get_status())
                    return

                # --- Simulation Commands (Allowed in ANY state) ---
                if cmd == 'simulate_button':
                    btn_id = int(data.get('btn_id'))
                    self.logger.info(f"[DEBUG] Simulating Button {btn_id}")
                    self.sm.on_button_press(btn_id)
                    return

                if cmd == 'simulate_qzss':
                    report = data.get('report', "Simulation Report")
                    self.logger.info(f"[DEBUG] Simulating QZSS: {report}")
                    self.sm.on_qz1_message(report)
                    return

                if cmd == 'simulate_imu':
                    force = float(data.get('force', 1.5))
                    self.logger.info(f"[DEBUG] Simulating IMU: {force}G")
                    self.sm.on_imu_shake(force)
                    return

                # --- Control Commands (Restricted to NORMAL state) ---
                if self.sm.current_state != self.sm.STATE_NORMAL:
                     self.logger.warning("Ignored control (Not in NORMAL state)")
                     return

                # Handle set/toggle
                if cmd in ['set', 'toggle']:
                    relay_val = data.get('relay')
                    if relay_val is None:
                        self.logger.error("Missing relay ID")
                        return

                    relay = int(relay_val)

                    if cmd == 'set':
                        state = bool(data.get('state'))
                        self.sm.power.set_relay(relay, state)
                    elif cmd == 'toggle':
                        self.sm.power.toggle(relay)
                else:
                    self.logger.warning(f"Unknown command: {cmd}")

            except Exception as e:
                self.logger.error(f"Error handling control event: {e}")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_client, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sio.connected:
            self.sio.disconnect()

    def _run_client(self):
        # Retry loop
        while self.running:
            try:
                if not self.sio.connected:
                    self.sio.connect(self.server_url)
                    self.sio.wait() # Blocking
            except Exception:
                # self.logger.error(f"Connection Failed: {e}")
                time.sleep(5) # Retry interval

    def emit_status(self, status_dict):
        """
        Emit 's2c_status' event to server.
        status_dict: {1: True, 2: False ...}
        """
        if self.sio.connected:
            self.logger.info(f"Emitting Status: {status_dict}")
            self.sio.emit('s2c_status', status_dict)
