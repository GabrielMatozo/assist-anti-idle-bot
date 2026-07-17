import random
import threading
import time

from src.core.keys import press_random, toggle_caps
from src.core.mouse import jiggle


class ActivityEngine:
    def __init__(self):
        self.running = False
        self.thread = None
        self._config = {}

    def start(self, config: dict):
        self._config = config
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(2)

    def is_active(self) -> bool:
        return self.running and (self.thread is not None and self.thread.is_alive())

    def _loop(self):
        while self.running:
            try:
                interval = max(1, int(self._config.get("interval", 60)))

                if self._config.get("caps_lock"):
                    toggle_caps()

                if self._config.get("key_press"):
                    press_random(self._config)

                if self._config.get("mouse_jiggle"):
                    jiggle(amount=self._config.get("jiggle_amount", 3))

                variation = random.uniform(-0.1, 0.1) * interval
                wait = max(0.5, interval + variation)
                start = time.time()
                while time.time() - start < wait and self.running:
                    time.sleep(0.1)

            except Exception as e:
                print(f"[ActivityEngine] erro: {e}")
                time.sleep(1)
