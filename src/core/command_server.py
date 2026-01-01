import socket
import threading
import json
import logging

class CommandServer:
    def __init__(self, state_machine, host='127.0.0.1', port=65432):
        self.sm = state_machine
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.server_socket = None
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        self.logger.info(f"Command Server listening on {self.host}:{self.port}")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.logger.info("Command Server stopped")

    def _run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    with conn:
                        data = conn.recv(1024)
                        if data:
                            self._handle_command(data)
                except OSError:
                    break # Socket closed
        except Exception as e:
            self.logger.error(f"Server Error: {e}")

    def _handle_command(self, data):
        try:
            cmd_dict = json.loads(data.decode('utf-8'))
            self.logger.info(f"Received command: {cmd_dict}")

            # {"cmd": "toggle", "relay": 1}
            action = cmd_dict.get('cmd')

            if action == 'toggle':
                relay_id = int(cmd_dict.get('relay'))
                if self.sm.current_state == self.sm.STATE_NORMAL:
                     self.sm.power.toggle(relay_id)
                else:
                    self.logger.warning("Ignored command (Not in NORMAL state)")

            elif action == 'set':
                relay_id = int(cmd_dict.get('relay'))
                state = bool(cmd_dict.get('state'))
                if self.sm.current_state == self.sm.STATE_NORMAL:
                    self.sm.power.set_relay(relay_id, state)
                else:
                    self.logger.warning("Ignored command (Not in NORMAL state)")

        except json.JSONDecodeError:
            self.logger.error("Invalid JSON received")
        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
