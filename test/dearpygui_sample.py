# sudo apt install fonts-noto-cjk

import dearpygui.dearpygui as dpg
import os

# --- 設定項目 ---
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SIZE = 18


def btn_callback(sender, app_data):
    current_val = dpg.get_value("input_text")
    dpg.set_value("output_label", f"入力された内容: {current_val}")
    print(f"ターミナル出力: {current_val}")


dpg.create_context()

# --- フォントのロード処理 ---
with dpg.font_registry():
    if os.path.exists(FONT_PATH):
        with dpg.font(FONT_PATH, FONT_SIZE) as default_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
        dpg.bind_font(default_font)
        print(f"フォントをロードしました: {FONT_PATH}")
    else:
        print(f"エラー: フォントファイルが見つかりません: {FONT_PATH}")

# --- GUIの定義 ---
dpg.create_viewport(title='RPi Zero 2 W - DPG Test', width=600, height=400)

with dpg.window(label="メインウィンドウ", width=580, height=380, pos=(10, 10)):
    dpg.add_text("【Raspberry Pi Zero 2 W 動作テスト】")
    dpg.add_text("Dear PyGuiで日本語を表示しています。", color=(0, 255, 255))

    dpg.add_separator()
    dpg.add_spacer(height=10)

    # 入力とボタン
    dpg.add_input_text(label="ここに入力", tag="input_text",
                       default_value="こんにちは世界")
    dpg.add_button(label="コンソールに出力してラベル更新", callback=btn_callback)
    dpg.add_text("", tag="output_label", color=(255, 200, 100))

    dpg.add_spacer(height=20)

    # グラフ（修正箇所：軸の定義方法を変更）
    with dpg.plot(label="サイン波テスト", height=150, width=-1):
        dpg.add_plot_legend()

        # X軸（withを使わず定義）
        dpg.add_plot_axis(dpg.mvXAxis, label="時間")

        # Y軸（withを使わず、IDを変数に保存）
        y_axis_id = dpg.add_plot_axis(dpg.mvYAxis, label="値")

        # データ生成
        x_data = [x/10.0 for x in range(0, 100)]
        y_data = [0.5 * x for x in x_data]

        # データをY軸に関連付けて追加 (parent引数を使用)
        dpg.add_line_series(x_data, y_data, label="テストデータ", parent=y_axis_id)

# --- アプリケーションの実行 ---
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
