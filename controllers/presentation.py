import pyautogui

class PresentationController:
    def next_slide(self):
        pyautogui.press('right')

    def prev_slide(self):
        pyautogui.press('left')

    def zoom_in(self):
        pyautogui.hotkey('ctrl', '+')

    def zoom_out(self):
        pyautogui.hotkey('ctrl', '-')
