import pyautogui
import time

def typing(response):
    pyautogui.write(response, interval=0.01)
