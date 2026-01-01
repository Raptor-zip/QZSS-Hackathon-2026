import serial
import threading
import time
import logging
# Placeholder for azarashi import. Expected usage based on research.
try:
    import azarashi
except ImportError:
    azarashi = None
    logging.warning("azarashi library not found. QZ1Handler will not decode messages.")

class QZ1Handler:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, callback=None):
        self.port = port
        self.baudrate = baudrate
        self.callback = callback
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"QZ1Handler started on {self.port}")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("QZ1Handler stopped")

    def _read_loop(self):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                while self.running:
                    line = ser.readline()
                    if line:
                        try:
                            decoded_line = line.decode('utf-8', errors='ignore').strip()
                            if decoded_line.startswith('$'): # NMEA sentence
                                self._process_nmea(decoded_line)
                            # Add support for binary if needed
                        except Exception as e:
                            self.logger.error(f"Error reading/decoding line: {e}")
        except serial.SerialException as e:
            self.logger.error(f"Serial port error: {e}")

    def _process_nmea(self, nmea_sentence):
        # Specific check for QZSS signals if needed (e.g., $QZQSM)
        # Using azarashi to decode
        if azarashi:
            try:
                # Assuming azarashi.decode takes the raw sentence or bytes
                # This part is speculative based on library description
                # If azarashi expects specific format (like binary payload), extraction is needed.
                # Common QZSS NMEA: $QZQSM,55,53,163606,20,01,135...*hh

                # Check for QZQSM or similar DCR NMEA content
                if "QZQSM" in nmea_sentence:
                   reports = azarashi.decode(nmea_sentence)
                   # azarashi might return a list of reports or a single report
                   for report in reports:
                       if self.callback:
                           self.callback(report)
            except Exception as e:
                self.logger.debug(f"Failed to decode with azarashi: {e}")

if __name__ == "__main__":
    # Test stub
    def print_alert(report):
        print(f"Alert received: {report}")

    logging.basicConfig(level=logging.INFO)
    handler = QZ1Handler(callback=print_alert)
    # handler.start() # Commented out to avoid auto-run issues
