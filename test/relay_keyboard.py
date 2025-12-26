from gpiozero import OutputDevice
import sys

# --- 設定部分 ---

# リレーのGPIO設定 (BCM番号)
# active_high=True: High(3.3V)でON。
# 一般的なリレーモジュールは Low(0V)でON の場合が多いです。
# その場合は active_high=False に変更してください。
relay1 = OutputDevice(4,  active_high=True, initial_value=False)
relay2 = OutputDevice(17, active_high=True, initial_value=False)
relay3 = OutputDevice(27, active_high=True, initial_value=False)
relay4 = OutputDevice(22, active_high=True, initial_value=False)

# リレーをリストにまとめて管理しやすくする
relays = {
    '1': relay1,
    '2': relay2,
    '3': relay3,
    '4': relay4
}

# --- メイン処理 ---


def print_status():
    """現在のリレーの状態を表示"""
    status_msg = []
    for key, r in relays.items():
        state = "ON" if r.value else "OFF"
        status_msg.append(f"R{key}:{state}")
    print(f"現在: [{' | '.join(status_msg)}]")


print("--- リレー制御テスト (キーボード入力) ---")
print("コマンドを入力して Enter を押してください:")
print(" [1] Relay 1 切替")
print(" [2] Relay 2 切替")
print(" [3] Relay 3 切替")
print(" [4] Relay 4 切替")
print(" [a] 全て ON")
print(" [z] 全て OFF")
print(" [q] 終了")
print("---------------------------------------")

try:
    while True:
        # ユーザー入力を待つ
        cmd = input("コマンド >> ").strip().lower()

        if cmd in relays:
            # 1~4が入力された場合、対応するリレーを反転
            target_relay = relays[cmd]
            target_relay.toggle()
            state = "ON" if target_relay.value else "OFF"
            print(f"-> Relay {cmd} を {state} にしました。")

        elif cmd == 'a':
            print("-> 全てのリレーを ON にします。")
            for r in relays.values():
                r.on()

        elif cmd == 'z':
            print("-> 全てのリレーを OFF にします。")
            for r in relays.values():
                r.off()

        elif cmd == 'q':
            print("終了します。")
            break

        else:
            print("無効なコマンドです。1-4, a, z, q のいずれかを入力してください。")

        # 現在の状態を表示
        print_status()

except KeyboardInterrupt:
    print("\n強制終了。安全のため全リレーをOFFにします。")
    for r in relays.values():
        r.off()
    sys.exit()
