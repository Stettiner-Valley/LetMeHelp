import pyautogui
import time


def activate_application(application_name):
    execute_key_commands(['command', 'space'])
    time.sleep(0.5)
    pyautogui.typewrite(application_name)
    time.sleep(0.5)
    pyautogui.press('enter')


def execute_key_commands(key_commands):
    pyautogui.hotkey(*key_commands, interval=0.1)



