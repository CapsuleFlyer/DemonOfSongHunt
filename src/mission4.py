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
