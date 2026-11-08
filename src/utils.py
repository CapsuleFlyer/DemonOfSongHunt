"""Helpers from the Corps blacksmith. Use them as they are."""
import time

def read_chunks(path, size=4096):
    """Yields the file in pieces of `size` characters. Use this for Mission 1."""
    with open(path) as f:
        while True:
            chunk = f.read(size)
            if not chunk:
                return
            yield chunk

def read_text(path):
    with open(path) as f:
        return f.read().strip()

class Timer:
    """with Timer() as t: ...   then t.seconds"""
    def __enter__(self):
        self.start = time.perf_counter(); return self
    def __exit__(self, *a):
        self.seconds = time.perf_counter() - self.start
