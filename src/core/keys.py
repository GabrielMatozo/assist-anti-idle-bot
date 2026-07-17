import random
import time
import pyautogui


ALL_KEYS = {
    "f15": "f15",
    "shift": "shift",
    "alt": "alt",
    "ctrl": "ctrl",
}


def press_random(config: dict):
    active_keys = [
        ALL_KEYS[k] for k, v in config.get("keys", {}).items() if v
    ]
    if not active_keys:
        return

    hold = max(0.05, min(1.0, config.get("hold_time", 0.1)))
    key = random.choice(active_keys)
    pyautogui.keyDown(key)
    time.sleep(hold)
    pyautogui.keyUp(key)


def toggle_caps():
    pyautogui.press("capslock")
    time.sleep(0.3)
    pyautogui.press("capslock")
