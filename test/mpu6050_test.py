import smbus2
import time
import math

# MPU6050のレジスタアドレス
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

# I2Cアドレス (デフォルトは0x68)
Device_Address = 0x68

# I2Cバスの取得 (Raspberry Piは通常バス1)
bus = smbus2.SMBus(1)


def MPU_Init():
    # サンプルレートの設定
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    # 電源管理レジスタの設定 (スリープ解除)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    # 設定レジスタ
    bus.write_byte_data(Device_Address, CONFIG, 0)

    # ジャイロ設定 (±250deg/s)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    # 割り込み許可
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)


def read_raw_data(addr):
    # 上位8ビットと下位8ビットを読み込んで16ビットにする
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)

    # 2つの値を結合
    value = ((high << 8) | low)

    # 符号付き16ビット整数として処理
    if (value > 32768):
        value = value - 65536
    return value


# 初期化
try:
    MPU_Init()
    print("MPU6050 初期化完了")
except Exception as e:
    print(f"エラー: MPU6050が見つかりません。配線を確認してください。\n{e}")
    exit()

print("計測開始 (Ctrl+C で終了)")
print("-" * 50)

try:
    while True:
        # 加速度の読み取り
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)

        # ジャイロの読み取り
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        # 生データを物理量に変換
        # 加速度: デフォルト設定(±2g)では 16384 LSB/g
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0

        # ジャイロ: デフォルト設定(±250deg/s)では 131 LSB/(deg/s)
        Gx = gyro_x / 131.0
        Gy = gyro_y / 131.0
        Gz = gyro_z / 131.0

        # 結果を表示 (\033[K は行クリアのエスケープシーケンスで見やすくするため)
        print(
            f"Accel [g]: X={Ax:.2f}, Y={Ay:.2f}, Z={Az:.2f} | Gyro [deg/s]: X={Gx:.2f}, Y={Gy:.2f}, Z={Gz:.2f}\033[K", end="\r")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n終了します")
