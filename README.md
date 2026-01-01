# フェーズフリー防災電源タップ (QZSS + Pi)

本プロジェクトは、Raspberry Pi Zero 2 W と QZSS（みちびき）の「災危通報」を利用した、フェーズフリーな防災電源タップのシステムです。

## 機能
- **平常時 (Phase 1)**: 大きなデジタル時計を表示。リレーはON（電源供給中）。QZSSと地震計を監視。
- **緊急時 (Phase 2)**:
  - トリガー: QZSS 緊急地震速報/津波警報 または 強い揺れ（MPU6050）を検知。
  - 動作: **即時電源遮断** (全リレーOFF)。
  - 警報: 画面が赤くなり、警告テキスト表示。大音量アラーム。
- **復旧**: 物理ボタンによる手動リセットで電源復旧。

## 必要ハードウェア
- **Raspberry Pi Zero 2 W**
- **QZ1** (みちびき受信機) -> USB
- **MPU6050** (IMU / 加速度センサ) -> I2C (GPIO 2, 3)
- **4チャンネル リレーモジュール** -> GPIO 4, 17, 27, 22
- **プッシュボタン (5個)** -> GPIO 5, 6, 13, 19, 26
- **スピーカー/ブザー** -> PWM (GPIO 12)
- **ディスプレイ** -> コンポジット または HDMI

## インストール方法

1. システム依存関係のインストール:
   ```bash
   sudo apt install fonts-noto-cjk libopenjp2-7
   ```
2. Pythonライブラリのインストール:
   ```bash
   pip install -r requirements.txt
   ```

3. I2Cとシリアルの有効化:
   - `sudo raspi-config` -> Interface Options

## 使い方

メインアプリの実行:
```bash
source .venv/bin/activate
python3 src/main.py
```

Webコントローラの実行（別ターミナルで）:
```bash
cd web
npm start
```

スマホから `http://<ラズパイのIP>:3000` にアクセスしてください。

## 設定
- `src/main.py` でボタン割り当てを変更可能。
- `src/hw/imu_handler.py` で震動検知の閾値を調整可能。
