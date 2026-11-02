"""Mission 1 — The Crow's Alarm (KMP).   Run: python mission1.py"""
from matchers import compute_prefix_function, kmp_resume
from utils import read_chunks

FILE = "../data/crow_log.txt"
ALARM = "KAKAKA"

pi = compute_prefix_function(ALARM)
print("pi =", pi)

all_shifts = []
q = 0        # kmp state, carried from one chunk to the next so split caws still count
offset = 0   # how many characters came before this chunk

for chunk in read_chunks(FILE, 4096):
    q, found, _ = kmp_resume(chunk, ALARM, pi, q, offset)
    all_shifts += found
    offset += len(chunk)  # next chunk starts after this one

print("Alarm count:", len(all_shifts))
print("First 10 shifts:", all_shifts[:10])
