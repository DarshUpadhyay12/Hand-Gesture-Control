import pyautogui

class MediaController:
    def play_pause(self):
        pyautogui.press('playpause')

    def next_track(self):
        pyautogui.press('nexttrack')

    def prev_track(self):
        pyautogui.press('prevtrack')

    def mute(self):
        pyautogui.press('volumemute')
        
    def skip_forward(self):
        pyautogui.press('right')
        
    def skip_backward(self):
        pyautogui.press('left')
