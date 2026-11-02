# Demon Hunt — what I changed

Everything below is the exact code that now sits in `starter/`. Files not listed (`utils.py`, `test_matchers.py`) were not touched.
Function names and signatures are the starter's, only the bodies were filled in. Variables are camelCase, comments are short and lowercase.

## How the pieces work (for the viva)

- **naive**: try every shift s, compare P[j] with T[s+j] until a mismatch or j reaches m.
- **rabin-karp**: hash = sum of ord(ch) * d^(position) mod q. `h = d^(m-1) mod q` is the weight of the leading digit, so rolling is `t = (d*(t - ord(T[s])*h) + ord(T[s+m])) mod q`. Hash hit -> verify char by char. Verify fails -> spurious hit.
- **prefix function (pi)**: `k` is the length of the current matched prefix. On a mismatch, `k = pi[k-1]` falls back to the next best prefix. `pi[i] = k`.
- **kmp_resume**: same loop but q is passed in and returned, so a match split across two chunks still completes. `offset + i - m + 1` turns the local index into a file-wide shift. After a match `q = pi[q-1]` keeps overlaps.
- **transition function (delta)**: for state q and char a, find the biggest k so that P[0..k) is a suffix of P[0..q)+a. That k is delta[q][a]. States run 0..m.
- **fa_match**: one lookup per character, `q = delta[q][ch]`, and q == m means a match ends here (shift = i - m + 1).

## Results when run

Tests: every line in `python test_matchers.py` says PASS.

**Mission 1** (`pi = [0, 0, 1, 2, 3, 4]`): 415 alarms, first 10 shifts `[8620, 8622, 8624, 39118, 39126, 88124, 88132, 90213, 90215, 90217]`.

**Mission 2**: reverse complement of the marker is `GAATCTGTAATC`. Only `sample_07.txt` has hits: 0 forward, 3 reverse. So the demon is sample_07. All other samples have 0 and 0.

**Mission 3**: zenitsu 89.00%, kanao 31.86%, inosuke 14.96%, tanjiro 0.00%, genya 0.00%.

**Bonus** (T = a x 100,000, P = a x 99 + b):

| matcher | comparisons | time |
|---|---|---|
| rabin-karp | 0 | ~0.02 s |
| automaton | 100,000 | ~0.02 s |
| kmp | 199,901 | ~0.02 s |
| naive | 9,990,100 | ~0.9 s |

Rabin-Karp has 0 comparisons because no window hash equals the hash of P, so it never has to verify. Only naive is the clear loser here. Run it yourself for your own timings since they vary by machine.

**Mission 3 two-liner for the report (edit into your own words):**
The detector only counts a stretch as copied if a whole 40-character window matches the manual exactly. A trainee who swapped words breaks the window every time a changed word lands inside it, and the short unchanged stretches between edits never fill a full window, so their copying is undercounted.

---

## The code

### Step 0 — `starter/matchers.py`

```python
"""
Demon Slayer Corps — The String Hunt
Your four techniques (matchers). Fill in every function marked TODO,
following the pseudocode from Lectures 7, 8 and 9.

Rules:
  * Shifts are 0-based: P occurs with shift s if T[s:s+m] == P.
  * Do NOT use str.find, the `in` operator on strings, str.count, re, or any other
    built-in search inside these functions. Compare characters one by one.
  * "comparisons" = how many times you compare one character of T with one character of P.

Check your work with:  python test_matchers.py
"""


def naive_match(T, P):
    """Lecture 7. Slide P over T one position at a time.
    Returns (shifts, comparisons)."""
    n = len(T)
    m = len(P)
    shifts = []
    comparisons = 0

    for s in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1  # one char of T vs one char of P
            if T[s + j] != P[j]:
                break  # mismatch, slide to the next shift
            j += 1
        if j == m:  # made it all the way through P
            shifts.append(s)

    return shifts, comparisons


def rabin_karp_match(T, P, d=256, q=101):
    """Lecture 7. Use ord(ch) as the digit value of a character.
    On every hash hit, verify character by character.
    Returns (shifts, comparisons, spurious_hits)."""
    n = len(T)
    m = len(P)
    shifts = []
    comparisons = 0
    spuriousHits = 0

    if m > n:  # pattern longer than text, nothing to find
        return shifts, comparisons, spuriousHits

    h = pow(d, m - 1, q)  # d^(m-1) mod q, used to remove the leading digit
    pHash = 0
    tHash = 0

    # hash of P and of the first window of T
    for i in range(m):
        pHash = (d * pHash + ord(P[i])) % q
        tHash = (d * tHash + ord(T[i])) % q

    for s in range(n - m + 1):
        if pHash == tHash:
            # hash hit, verify char by char
            j = 0
            while j < m:
                comparisons += 1
                if T[s + j] != P[j]:
                    break
                j += 1
            if j == m:
                shifts.append(s)
            else:
                spuriousHits += 1  # hash matched but the text didn't

        # roll the hash to the next window (drop T[s], add T[s+m])
        if s < n - m:
            tHash = (d * (tHash - ord(T[s]) * h) + ord(T[s + m])) % q

    return shifts, comparisons, spuriousHits


def compute_prefix_function(P):
    """Lecture 8. Returns the list pi, where pi[i] is the length of the longest
    proper prefix of P[0..i] that is also a suffix of it.
    Example: compute_prefix_function("ababaca") == [0, 0, 1, 2, 3, 0, 1]"""
    m = len(P)
    pi = [0] * m
    k = 0  # length of the current matched prefix

    for i in range(1, m):
        while k > 0 and P[k] != P[i]:
            k = pi[k - 1]  # fall back to the next best prefix
        if P[k] == P[i]:
            k += 1
        pi[i] = k

    return pi


def kmp_resume(T, P, pi, q, offset):
    """Lecture 8, with one change: the matcher starts in state q instead of 0,
    and `offset` is the position of T[0] inside the whole file.
    This lets you feed a big file in chunks and carry q from one chunk to the next.
    After a full match, set q = pi[q - 1] so overlapping matches are found.
    Returns (q_at_the_end, shifts_found, comparisons)."""
    n = len(T)
    m = len(P)
    shifts = []
    comparisons = 0

    for i in range(n):
        # on a mismatch, fall back using pi
        while q > 0 and P[q] != T[i]:
            comparisons += 1
            q = pi[q - 1]

        comparisons += 1  # the compare that ends the loop (match, or q is 0)
        if P[q] == T[i]:
            q += 1

        if q == m:
            shifts.append(offset + i - m + 1)  # offset makes the shift global
            q = pi[q - 1]  # keep going so overlaps are found

    return q, shifts, comparisons


def kmp_match(T, P):
    """Whole-text KMP. Already done for you: it just calls kmp_resume once."""
    pi = compute_prefix_function(P)
    _, shifts, comparisons = kmp_resume(T, P, pi, 0, 0)
    return shifts, comparisons


def compute_transition_function(P, alphabet):
    """Lecture 9. Returns delta as a list of dicts: delta[q][a] = next state.
    There are len(P) + 1 states (0 .. m)."""
    m = len(P)
    delta = []

    for q in range(m + 1):
        row = {}
        for a in alphabet:
            # biggest k such that P[0..k) is a suffix of P[0..q) + a
            k = min(m, q + 1)
            while k > 0:
                same = True
                for j in range(k):
                    pos = q + 1 - k + j  # position inside P[0..q) + a
                    if pos == q:
                        ch = a  # the extra char at the end
                    else:
                        ch = P[pos]
                    if P[j] != ch:
                        same = False
                        break
                if same:
                    break
                k -= 1
            row[a] = k
        delta.append(row)

    return delta


def fa_match(T, delta, m):
    """Lecture 9. Start at q = 0 and do q = delta[q][T[i]] for every character.
    A character not in the alphabet sends you back to state 0.
    Returns (shifts, steps) where steps = number of table lookups."""
    shifts = []
    steps = 0
    q = 0

    for i in range(len(T)):
        steps += 1  # one table lookup
        q = delta[q].get(T[i], 0)  # not in alphabet -> back to 0
        if q == m:
            shifts.append(i - m + 1)

    return shifts, steps
```

### Mission 1 — `starter/mission1.py`

```python
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
```

### Mission 2 — `starter/mission2.py`

```python
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
```

### Mission 3 — `starter/mission3.py`

```python
"""Mission 3 — The Copycat Slayer (Rabin-Karp).   Run: python mission3.py"""
import os
from utils import read_text

MANUAL = "../data/hashira_manual.txt"
FOLDER = "../data/trainee_reports"
K = 40          # window length in characters
D = 256

def clean_text(t):
    # lowercase, turn punctuation into spaces, collapse runs of spaces into one
    t = t.lower()
    cleaned = ""
    lastWasSpace = True  # starts true so there's no leading space
    for ch in t:
        if ch.isalnum():
            cleaned += ch
            lastWasSpace = False
        elif not lastWasSpace:  # anything else counts as a space, only add one
            cleaned += " "
            lastWasSpace = True
    return cleaned.strip()

def copy_detect(manual, report, k=K, d=D, q=1_000_000_007):
    """
      1. Rolling-hash every k-character window of `manual`; store hash -> list of shifts.
      2. Roll the hash across `report`. On a hit, compare characters yourself
         (write the loop, no == on slices).
      3. Mark every report character covered by a verified window.
      4. similarity = covered characters / len(report) * 100
    Return similarity_percent."""
    nM = len(manual)
    nR = len(report)

    if nR < k or nM < k:  # no full window fits, nothing can be copied
        return 0.0

    h = pow(d, k - 1, q)  # d^(k-1) mod q for the rolling step

    # step 1, hash every window of the manual -> list of shifts
    manualHashes = {}
    wHash = 0
    for i in range(k):
        wHash = (d * wHash + ord(manual[i])) % q
    for s in range(nM - k + 1):
        if wHash not in manualHashes:
            manualHashes[wHash] = []
        manualHashes[wHash].append(s)
        if s < nM - k:  # roll to the next window
            wHash = (d * (wHash - ord(manual[s]) * h) + ord(manual[s + k])) % q

    # step 2 + 3, roll over the report, verify hits, mark covered chars
    covered = [False] * nR
    rHash = 0
    for i in range(k):
        rHash = (d * rHash + ord(report[i])) % q
    for s in range(nR - k + 1):
        if rHash in manualHashes:
            for mShift in manualHashes[rHash]:
                # verify char by char, hash hit could be a collision
                j = 0
                while j < k:
                    if report[s + j] != manual[mShift + j]:
                        break
                    j += 1
                if j == k:  # real copy, mark the whole window
                    for c in range(s, s + k):
                        covered[c] = True
                    break  # no need to check other manual shifts
        if s < nR - k:
            rHash = (d * (rHash - ord(report[s]) * h) + ord(report[s + k])) % q

    # step 4
    coveredCount = 0
    for c in covered:
        if c:
            coveredCount += 1
    return coveredCount / nR * 100

# clean the manual and every report, run copy_detect on each report,
# print each trainee's similarity and rank all five (highest first)
manual = clean_text(read_text(MANUAL))

scores = []   # (trainee, similarity)
for fileName in sorted(os.listdir(FOLDER)):
    report = clean_text(read_text(os.path.join(FOLDER, fileName)))
    trainee = fileName.replace("report_", "").replace(".txt", "")
    scores.append((trainee, copy_detect(manual, report)))

print("similarity per trainee")
for trainee, sim in scores:
    print(f"{trainee:<10} {sim:6.2f}%")

# sort highest first (simple selection sort so it's easy to follow)
ranked = scores[:]
for i in range(len(ranked)):
    best = i
    for j in range(i + 1, len(ranked)):
        if ranked[j][1] > ranked[best][1]:
            best = j
    ranked[i], ranked[best] = ranked[best], ranked[i]

print("\nranking (highest first)")
for place, (trainee, sim) in enumerate(ranked, start=1):
    print(f"{place}. {trainee:<10} {sim:6.2f}%")
```

### Bonus — `starter/mission4.py`

```python
"""BONUS — Breathing Styles Tournament (+10).   Run: python mission4.py"""
from matchers import *
from utils import Timer
import matplotlib
matplotlib.use("Agg")  # no window needed, just saves the png
import matplotlib.pyplot as plt

ARENA = ("a" * 100_000, "a" * 99 + "b")   # T, P

T, P = ARENA
results = {}   # name -> (comparisons, seconds)

# naive
with Timer() as t:
    shifts, comps = naive_match(T, P)
results["naive"] = (comps, t.seconds)

# rabin-karp
with Timer() as t:
    shifts, comps, spurious = rabin_karp_match(T, P)
results["rabin-karp"] = (comps, t.seconds)

# kmp
with Timer() as t:
    shifts, comps = kmp_match(T, P)
results["kmp"] = (comps, t.seconds)

# automaton, building delta is part of the cost so it's inside the timer
with Timer() as t:
    delta = compute_transition_function(P, "ab")
    shifts, comps = fa_match(T, delta, len(P))
results["automaton"] = (comps, t.seconds)  # steps = table lookups

# leaderboard, fewest comparisons first
names = sorted(results, key=lambda n: results[n][0])
print("rank  name         comparisons   seconds")
for rank, name in enumerate(names, start=1):
    print(f"{rank:<5} {name:<12} {results[name][0]:>11}   {results[name][1]:.4f}")

# one figure with two bar charts, symlog scale because naive is way bigger and rabin-karp is 0
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].bar(names, [results[n][0] for n in names])
axes[0].set_title("comparisons (symlog scale)")
axes[0].set_yscale("symlog")
axes[1].bar(names, [results[n][1] for n in names])
axes[1].set_title("time in seconds")
plt.tight_layout()
plt.savefig("tournament.png")
print("chart saved to tournament.png")
```
