import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
import numpy as np
from loguru import logger

class SystemController:
    def __init__(self):
        # Volume initialization
        try:
            import comtypes
            comtypes.CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            self.vol_range = self.volume.GetVolumeRange()
            self.min_vol = self.vol_range[0]
            self.max_vol = self.vol_range[1]
        except Exception as e:
            logger.error(f"Failed to initialize volume control: {e}")
            self.volume = None

    def set_volume(self, length, min_len=20, max_len=150):
        if self.volume:
            vol = np.interp(length, [min_len, max_len], [self.min_vol, self.max_vol])
            try:
                self.volume.SetMasterVolumeLevel(vol, None)
            except Exception as e:
                pass

    def set_brightness(self, length):
        try:
            # Map length (approx 15 to 150) to brightness (0 to 100)
            brightness = np.interp(length, [15, 150], [0, 100])
            sbc.set_brightness(int(brightness))
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")

    def open_youtube(self):
        import webbrowser
        webbrowser.open('https://youtube.com')

    def open_file_manager(self):
        pyautogui.hotkey('win', 'e')

    def open_win_h(self):
        pyautogui.hotkey('win', 'h')

    def close_current_app(self):
        pyautogui.hotkey('alt', 'f4')

    def open_cricbuzz(self):
        import webbrowser
        webbrowser.open('https://www.cricbuzz.com')

    def open_streaming(self):
        import webbrowser
        webbrowser.open('https://www.bestfreestreaming.org')

    def alt_tab(self):
        pyautogui.hotkey('alt', 'tab')

    def open_brave_chatgpt(self):
        import webbrowser
        import os
        try:
            paths = [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
            ]
            brave_path = None
            for p in paths:
                if os.path.exists(p):
                    brave_path = p
                    break
            if brave_path:
                webbrowser.register('brave', None, webbrowser.BackgroundBrowser(brave_path))
                webbrowser.get('brave').open('https://chatgpt.com')
            else:
                webbrowser.open('https://chatgpt.com')
            
            import time
            time.sleep(2)
            pyautogui.hotkey('win', 'up') # maximize
        except Exception:
            webbrowser.open('https://chatgpt.com')

    def close_all_apps_gracefully(self):
        try:
            import pygetwindow as gw
            import time
            
            # Show desktop first to minimize everything, then close them gracefully
            pyautogui.hotkey('win', 'd')
            time.sleep(0.5)
            
            for win in gw.getAllWindows():
                if win.title != "" and win.visible and win.title != "Hand Gesture Control":
                    try:
                        win.close()
                    except:
                        pass
        except Exception as e:
            logger.error(f"Failed to close all apps: {e}")

    def screenshot(self):
        pyautogui.screenshot("screenshot.png")
        logger.info("Screenshot taken.")

    def switch_apps(self):
        pyautogui.hotkey('alt', 'tab')
        
    def show_desktop(self):
        pyautogui.hotkey('win', 'd')

    def close_window(self):
        pyautogui.hotkey('alt', 'f4')
