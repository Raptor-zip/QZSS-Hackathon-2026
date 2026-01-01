import dearpygui.dearpygui as dpg
import time
import os
import logging
import threading

# Configuration based on sample
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SIZE_CLOCK = 100
FONT_SIZE_NORMAL = 24
FONT_SIZE_ALERT = 40

class AppWindow:
    def __init__(self, state_machine):
        self.sm = state_machine
        self.logger = logging.getLogger(__name__)
        self.running = True

        dpg.create_context()
        self._load_fonts()
        self._setup_ui()
        dpg.create_viewport(title='QZSS Disaster Power Strip', width=800, height=480) # Adjust for Pi Display
        dpg.setup_dearpygui()

    def _load_fonts(self):
        with dpg.font_registry():
            if os.path.exists(FONT_PATH):
                # Normal Font
                with dpg.font(FONT_PATH, FONT_SIZE_NORMAL) as self.font_normal:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)

                # Clock Font
                with dpg.font(FONT_PATH, FONT_SIZE_CLOCK) as self.font_clock:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)

                # Alert Font
                with dpg.font(FONT_PATH, FONT_SIZE_ALERT) as self.font_alert:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)

                dpg.bind_font(self.font_normal)
            else:
                self.logger.error(f"Font not found: {FONT_PATH}")

    def _setup_ui(self):
        with dpg.window(tag="main_window", label="Main", no_title_bar=True, no_resize=True, no_move=True):
            # Clock Display
            dpg.add_text("00:00:00", tag="clock_text")
            if hasattr(self, 'font_clock'):
                dpg.bind_item_font("clock_text", self.font_clock)

            dpg.add_separator()

            # Status Area
            dpg.add_text("状態: 正常", tag="status_text")
            dpg.add_text("QZSS: 待機中...", tag="qzss_status")
            dpg.add_text("震動監視: 監視中...", tag="imu_status")
            dpg.add_separator()
            dpg.add_text("コンセント状態:", tag="relay_header")
            dpg.add_text("1: ? | 2: ? | 3: ? | 4: ?", tag="relay_status")

            # Alert Group (Hidden by default)
            with dpg.group(tag="alert_group", show=False):
                dpg.add_spacer(height=20)
                dpg.add_text("緊急地震速報 / 警報", tag="alert_title", color=(255, 0, 0))
                if hasattr(self, 'font_alert'):
                    dpg.bind_item_font("alert_title", self.font_alert)
                dpg.add_text("詳細情報なし", tag="alert_body")

    def update(self):
        # Update Clock
        current_time = time.strftime("%H:%M:%S")
        dpg.set_value("clock_text", current_time)

        # Check State Machine (Thread-safe reading assumed/needed)
        current_state = self.sm.current_state
        state_jp = {
            "BOOT": "起動中",
            "NORMAL": "正常",
            "ALERT": "警報発令中",
            "RECOVERY": "復旧待機"
        }.get(current_state, current_state)

        dpg.set_value("status_text", f"状態: {state_jp}")

        # Update Relay Status
        if hasattr(self.sm, 'power'):
             status = self.sm.power.get_status()
             status_str_list = []
             for k in sorted(status.keys()):
                 s = "ON" if status[k] else "OFF"
                 status_str_list.append(f"{k}: {s}")
             dpg.set_value("relay_status", " | ".join(status_str_list))

        # UI Logic for States
        if current_state == "ALERT":
            dpg.configure_item("main_window", no_background=False) # Red BG? DPG doesn't support easy bg color change per window dynamically without themes.
            # Using simple text color/visibility for now
            dpg.show_item("alert_group")
            # Update Alert Text if available
            if self.sm.alert_message:
                 dpg.set_value("alert_body", self.sm.alert_message)
        else:
            dpg.hide_item("alert_group")

        dpg.render_dearpygui_frame()

    def run(self):
        dpg.show_viewport()
        while dpg.is_dearpygui_running() and self.running:
            self.update()
        dpg.destroy_context()
        self.sm.stop() # Stop core logic when GUI closes

    def close(self):
        self.running = False

