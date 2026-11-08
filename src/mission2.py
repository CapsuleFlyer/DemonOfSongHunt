"""Mission 2 — Tamayo's Blood Lab (finite automaton).   Run: python mission2.py"""
import os
from matchers import compute_transition_function, fa_match
from utils import read_text

FOLDER = "../data/blood_samples"
DEMON_MARKER = "GATTACAGATTC"
ALPHABET = "ACGT"

def reverse_complement(s):
    # swap A<->T and C<->G, then reverse
    swap = {"A": "T", "T": "A", "C": "G", "G": "C"}
    result = ""
    for ch in s:
        result += swap[ch]
    return result[::-1]

# build delta for the marker and print it as a table (one row per state)
delta = compute_transition_function(DEMON_MARKER, ALPHABET)
print("delta for", DEMON_MARKER)
print("state  " + "  ".join(ALPHABET))
for state in range(len(delta)):
    print(f"{state:>5}  " + "  ".join(str(delta[state][a]) for a in ALPHABET))

# same thing for the reverse complement strand
revMarker = reverse_complement(DEMON_MARKER)
revDelta = compute_transition_function(revMarker, ALPHABET)
print("\nreverse complement of the marker:", revMarker)

# run both tables on every sample
results = []   # (file name, forward matches, reverse matches)
print("\nfile            forward  reverse")
for fileName in sorted(os.listdir(FOLDER)):
    dna = read_text(os.path.join(FOLDER, fileName))
    fwdShifts, _ = fa_match(dna, delta, len(DEMON_MARKER))
    revShifts, _ = fa_match(dna, revDelta, len(revMarker))
    results.append((fileName, len(fwdShifts), len(revShifts)))
    print(f"{fileName:<15} {len(fwdShifts):>7}  {len(revShifts):>7}")

# the demon is the sample with the most marker hits overall
demon = results[0]
for r in results:
    if r[1] + r[2] > demon[1] + demon[2]:
        demon = r
print("\nThe demon is:", demon[0], f"(forward {demon[1]}, reverse {demon[2]})")
