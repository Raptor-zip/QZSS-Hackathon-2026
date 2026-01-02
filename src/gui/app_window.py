import dearpygui.dearpygui as dpg
import time
import os
import logging
import threading

# Configuration
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SIZE_CLOCK = 160 # Bigger Clock
FONT_SIZE_NORMAL = 24
FONT_SIZE_STATUS = 32
FONT_SIZE_RELAY = 40
FONT_SIZE_ALERT_TITLE = 60
FONT_SIZE_ALERT_BODY = 36

class AppWindow:
    def __init__(self, state_machine):
        self.sm = state_machine
        self.logger = logging.getLogger(__name__)
        self.running = True
        self.current_screen = None # "NORMAL" or "ALERT"

        dpg.create_context()
        self._load_fonts()
        self._setup_ui()
        dpg.create_viewport(title='QZSS Disaster Power Strip', width=800, height=480)
        dpg.set_viewport_resize_callback(self._on_resize)
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

                # Status Font
                with dpg.font(FONT_PATH, FONT_SIZE_STATUS) as self.font_status:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)

                # Relay Font
                with dpg.font(FONT_PATH, FONT_SIZE_RELAY) as self.font_relay:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)

                # Alert Title Font
                with dpg.font(FONT_PATH, FONT_SIZE_ALERT_TITLE) as self.font_alert_title:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)

                # Alert Body Font
                with dpg.font(FONT_PATH, FONT_SIZE_ALERT_BODY) as self.font_alert_body:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)

                dpg.bind_font(self.font_normal)
            else:
                self.logger.error(f"Font not found: {FONT_PATH}")

    def _setup_ui(self):
        with dpg.window(tag="main_window", label="Main", no_title_bar=True, no_resize=True, no_move=True):
            dpg.set_primary_window("main_window", True)

            # --- SCREEN 1: NORMAL (Drawlist) ---
            with dpg.group(tag="group_normal"):
                with dpg.drawlist(width=800, height=480, tag="normal_drawlist"):
                     # Background (Optional, or just clear color)
                    # dpg.draw_rectangle((0,0), (800, 480), fill=(20, 20, 20), color=(20, 20, 20), tag="normal_bg")

                    # Text Items
                    dpg.draw_text((0, 0), "00:00:00", color=(255, 255, 255), size=120, tag="clock_draw")
                    dpg.draw_text((0, 0), "システム正常稼働中", color=(100, 200, 255), size=32, tag="status_draw")
                    dpg.draw_text((0, 0), "Relay Status Loading...", color=(100, 255, 100), size=40, tag="relay_draw")
                    dpg.draw_text((0, 0), "▼ 災害監視中 (QZSS/IMU)", color=(100, 100, 100), size=24, tag="footer_draw")

                    # Bind Fonts
                    if hasattr(self, 'font_clock'): dpg.bind_item_font("clock_draw", self.font_clock)
                    if hasattr(self, 'font_status'): dpg.bind_item_font("status_draw", self.font_status)
                    if hasattr(self, 'font_relay'): dpg.bind_item_font("relay_draw", self.font_relay)
                    if hasattr(self, 'font_normal'): dpg.bind_item_font("footer_draw", self.font_normal)

            # --- SCREEN 2: ALERT (Drawlist) ---
            with dpg.group(tag="group_alert", show=False):
                with dpg.drawlist(width=800, height=480, tag="alert_drawlist"):
                    dpg.draw_rectangle((0,0), (800, 480), fill=(200, 0, 0), color=(200, 0, 0), tag="alert_rect")

                    dpg.draw_text((0, 0), "警報発令", color=(255, 255, 0), size=60, tag="alert_header_draw")
                    dpg.draw_text((0, 0), "強い揺れ/緊急地震速報を検知しました", color=(255, 255, 255), size=36, tag="alert_body_1_draw")
                    dpg.draw_text((0, 0), "安全のため電源を遮断しました", color=(255, 255, 255), size=36, tag="alert_body_2_draw")
                    dpg.draw_text((0, 0), "安全確認後、ボタン1を押して復旧してください", color=(200, 200, 200), size=24, tag="alert_footer_draw")

                    if hasattr(self, 'font_alert_title'): dpg.bind_item_font("alert_header_draw", self.font_alert_title)
                    if hasattr(self, 'font_alert_body'):
                        dpg.bind_item_font("alert_body_1_draw", self.font_alert_body)
                        dpg.bind_item_font("alert_body_2_draw", self.font_alert_body)
                    if hasattr(self, 'font_normal'): dpg.bind_item_font("alert_footer_draw", self.font_normal)

    def _update_layout(self):
        """Recalculate positions based on viewport size"""
        w = dpg.get_viewport_client_width()
        h = dpg.get_viewport_client_height()

        # Resize Drawlists
        dpg.configure_item("normal_drawlist", width=w, height=h)
        dpg.configure_item("alert_drawlist", width=w, height=h)
        dpg.configure_item("alert_rect", pmax=(w, h))

        # Center Item Helper
        def center_item(tag, y_pct, font_ref):
            conf = dpg.get_item_configuration(tag)
            text = conf.get('text', '')
            font = 0
            if font_ref: font = font_ref

            size = dpg.get_text_size(text, font=font)
            if size:
                tw, th = size
            else:
                tw, th = 0, 0

            x = (w - tw) / 2
            y = (h * y_pct) - (th / 2)
            dpg.configure_item(tag, pos=(x, y))

        # Update Normal Layout
        center_item("clock_draw", 0.35, self.font_clock)
        center_item("status_draw", 0.60, self.font_status)
        center_item("relay_draw", 0.75, self.font_relay)
        center_item("footer_draw", 0.90, self.font_normal)

        # Update Alert Layout
        center_item("alert_header_draw", 0.20, self.font_alert_title)
        center_item("alert_body_1_draw", 0.45, self.font_alert_body)
        center_item("alert_body_2_draw", 0.55, self.font_alert_body)
        center_item("alert_footer_draw", 0.85, self.font_normal)

    def _on_resize(self, sender, app_data):
        self._update_layout()

    def update(self):
        current_time = time.strftime("%H:%M:%S")

        if self.sm.current_state != "ALERT":
            # Update Normal Screen
            if self.current_screen != "NORMAL":
                dpg.hide_item("group_alert")
                dpg.show_item("group_normal")
                self.current_screen = "NORMAL"
                self._update_layout() # Force initial layout

            # Update Text Content
            dpg.configure_item("clock_draw", text=current_time)

            # Status Text
            state_str = {
                "BOOT": "起動準備中...",
                "NORMAL": "システム正常稼働中",
                "RECOVERY": "復旧待機中..."
            }.get(self.sm.current_state, "不明")
            dpg.configure_item("status_draw", text=state_str)

            # Relay Status
            if hasattr(self.sm, 'power'):
                 status = self.sm.power.get_status()
                 # Format: 1:ON 2:OFF ...
                 # Using Symbols? ● ○
                 parts = []
                 for k in sorted(status.keys()):
                     sym = "ON" if status[k] else "OFF"
                     parts.append(f"{k}:{sym}")
                 dpg.configure_item("relay_draw", text="  ".join(parts))

            # Re-center (important if text length changes, e.g. 00:00:01 vs 10:00:00 usually same, but status might change)
            # Optimization: Only re-layout if text changed? For now, simple enough to run.
            # Running layout every frame is heavy? get_text_size might be fast.
            # Let's run it.
            self._update_layout()

        else:
            # ALERT Mode
            if self.current_screen != "ALERT":
                dpg.hide_item("group_normal")
                dpg.show_item("group_alert")
                self.current_screen = "ALERT"
                self._update_layout()

            msg = self.sm.alert_message
            if msg:
                dpg.configure_item("alert_body_1_draw", text=f"{msg}")
                self._update_layout()

        dpg.render_dearpygui_frame()

    def run(self):
        dpg.show_viewport()
        while dpg.is_dearpygui_running() and self.running:
            self.update()
        dpg.destroy_context()
        self.sm.stop()

    def close(self):
        self.running = False
