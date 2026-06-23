import threading
import time

class TaskScheduler:
    """Engine for scheduling background jobs."""
    def __init__(self):
        self.tasks = []
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _run_loop(self):
        while self.running:
            time.sleep(1)
