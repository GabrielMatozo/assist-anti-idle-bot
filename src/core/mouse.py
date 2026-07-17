import random
import pyautogui


def jiggle(amount: int = 3):
    a = max(1, abs(amount))
    dx = random.randint(-a, a)
    dy = random.randint(-a, a)
    pyautogui.moveRel(dx, dy, duration=0.1)
    pyautogui.moveRel(-dx, -dy, duration=0.1)
