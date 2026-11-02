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
