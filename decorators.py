import time
import threading
from collections import defaultdict

from database import AsyncDatabase


class Tracker:
    def __init__(self):
        self.metrics = defaultdict(lambda: {"calls": 0, "total_time": 0, "errors": 0})
        self.lock = threading.Lock()
        self.database = AsyncDatabase()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            self._increment_calls(func.__name__)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                self._increment_errors(func.__name__)
                raise e
            finally:
                elapsed_time = time.time() - start_time
                self._add_execution_time(func.__name__, elapsed_time)
                metrics = self.get_metrics(func.__name__)
                self.save_metrics(metrics)
            return result
        return wrapper

    def _increment_calls(self, func_name):
        with self.lock:
            self.metrics[func_name]["calls"] += 1

    def _increment_errors(self, func_name):
        with self.lock:
            self.metrics[func_name]["errors"] += 1

    def _add_execution_time(self, func_name, elapsed_time):
        with self.lock:
            self.metrics[func_name]["total_time"] += elapsed_time

    def get_metrics(self, func_name):
        with self.lock:
            data = self.metrics[func_name]
            avg_time = data["total_time"] / data["calls"] if data["calls"] else 0
            return {
                "Function": func_name,
                "Number of calls": data["calls"],
                "Average execution time": avg_time,
                "Number of errors": data["errors"],
            }
            
    def save_metrics(self, func_name):
        data = self.metrics[func_name]
        threading.Thread(target=self.database.save_metrics, args=(func_name, data)).start()

    def read_metrics(self, func_name):
        return self.database.read_metrics(func_name)


tracker = Tracker()
