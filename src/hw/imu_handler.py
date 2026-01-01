import smbus2
import math
import logging
import time
import threading

# MPU6050 Registers
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

class IMUHandler:
    def __init__(self, address=0x68, bus_num=1, threshold=2.0):
        self.address = address
        self.bus_num = bus_num
        self.logger = logging.getLogger(__name__)
        self.threshold = threshold
        self.callback = None
        self.running = False
        self.thread = None
        self.mock_mode = False
        try:
            self.bus = smbus2.SMBus(bus_num) # Requires I2C enabled
            self._init_mpu()
        except (PermissionError, FileNotFoundError, OSError) as e:
            self.logger.warning(f"Failed to access I2C bus: {e}. Switching to MOCK MODE.")
            self.mock_mode = True

    def _init_mpu(self):
        try:
            self.bus.write_byte_data(self.address, SMPLRT_DIV, 7)
            self.bus.write_byte_data(self.address, PWR_MGMT_1, 1)
            self.bus.write_byte_data(self.address, CONFIG, 0)
            self.bus.write_byte_data(self.address, GYRO_CONFIG, 24)
            self.bus.write_byte_data(self.address, INT_ENABLE, 1)
            self.logger.info("MPU6050 initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize MPU6050: {e}")

    def _read_raw_data(self, addr):
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr+1)
        value = ((high << 8) | low)
        if value > 32768:
            value = value - 65536
        return value

    def get_accel_data(self):
        if self.mock_mode:
            import random
            return 0.0, 0.0, 1.0 + random.uniform(-0.01, 0.01)

        try:
            Ax = self._read_raw_data(ACCEL_XOUT_H)
            Ay = self._read_raw_data(ACCEL_YOUT_H)
            Az = self._read_raw_data(ACCEL_ZOUT_H)

            # Simple conversion to G (assuming default range +/- 2G)
            Ax = Ax / 16384.0
            Ay = Ay / 16384.0
            Az = Az / 16384.0

            return Ax, Ay, Az
        except Exception as e:
            self.logger.error(f"Error reading accelerometer: {e}")
            return 0, 0, 0

    def start_monitoring(self, callback):
        self.callback = callback
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info("IMU monitoring started")

    def stop_monitoring(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _monitor_loop(self):
        while self.running:
            ax, ay, az = self.get_accel_data()
            total_g = math.sqrt(ax**2 + ay**2 + az**2)

            # Simple threshold check (Modify logic for better seismic detection)
            # Normal gravity is 1.0G. Earthquake would deviate significantly.
            if abs(total_g - 1.0) > self.threshold:
                if self.callback:
                    self.callback(total_g)
                time.sleep(1) # Debounce

            time.sleep(0.1)

if __name__ == "__main__":
    def alert(g):
        print(f"SHAKING DETECTED! G={g:.2f}")

    imu = IMUHandler()
    # imu.start_monitoring(alert)
